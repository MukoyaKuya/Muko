import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.crypto import salted_hmac
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import ContactSubmissionForm
from .models import FeaturedProject, ShopCategory, ShopItem, ShopSectionSettings


logger = logging.getLogger(__name__)


def get_client_ip(request):
    if getattr(settings, 'TRUST_X_FORWARDED_FOR', False):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            return forwarded.split(',', 1)[0].strip()
    return request.META.get('REMOTE_ADDR', '').strip()

class HomeView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_filter = self.request.GET.get('category', FeaturedProject.FILTER_ALL).lower()
        valid_filters = {
            FeaturedProject.FILTER_ALL,
            FeaturedProject.FILTER_WEB,
            FeaturedProject.FILTER_DESIGN,
        }
        if selected_filter not in valid_filters:
            selected_filter = FeaturedProject.FILTER_ALL

        featured_projects = FeaturedProject.objects.filter(
            is_published=True
        ).prefetch_related('gallery_images')
        if selected_filter != FeaturedProject.FILTER_ALL:
            featured_projects = featured_projects.filter(filter_group=selected_filter)

        context['featured_projects'] = featured_projects
        context['selected_project_filter'] = selected_filter
        context['project_filters'] = [
            {'value': FeaturedProject.FILTER_ALL, 'label': 'All'},
            {'value': FeaturedProject.FILTER_WEB, 'label': 'Web'},
            {'value': FeaturedProject.FILTER_DESIGN, 'label': 'Design'},
        ]
        context['shop_categories'] = ShopCategory.objects.filter(is_published=True)
        context['shop_section'] = ShopSectionSettings.objects.first()
        context['form'] = ContactSubmissionForm()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request') == 'true':
            return TemplateResponse(
                self.request,
                'core/partials/featured_projects.html',
                context,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)


class ShopHomeView(TemplateView):
    """Public entry point for the catalogue's top-level categories."""

    template_name = 'core/shop/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop_section'] = ShopSectionSettings.objects.first()
        context['shop_categories'] = ShopCategory.objects.filter(is_published=True)
        context['page_title'] = 'Shop | Muko'
        context['page_description'] = 'Browse Muko branding, software development, APIs, and digital services.'
        return context


class ShopCategoryView(TemplateView):
    """A published category and its published catalogue items."""

    template_name = 'core/shop/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = ShopCategory.objects.get(
                slug=kwargs['slug'],
                is_published=True,
            )
        except ShopCategory.DoesNotExist as exc:
            raise Http404('Shop category not found.') from exc

        context['category'] = category
        context['shop_items'] = category.items.filter(is_published=True)
        context['page_title'] = f'{category.name} | Shop | Muko'
        context['page_description'] = category.description
        return context


class ProjectDetailView(TemplateView):
    template_name = 'core/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs['slug']
        try:
            project = FeaturedProject.objects.prefetch_related('gallery_images').get(slug=slug, is_published=True)
        except FeaturedProject.DoesNotExist as exc:
            raise Http404('Project not found.') from exc

        context['project'] = project
        context['projects'] = FeaturedProject.objects.filter(is_published=True)
        context['page_title'] = f'{project.title} | Muko'
        context['page_description'] = project.card_summary
        return context


class ContactView(FormView):
    form_class = ContactSubmissionForm
    template_name = 'core/partials/contact_form.html'

    def post(self, request, *args, **kwargs):
        ip_address = get_client_ip(request) or 'unknown'
        fingerprint = salted_hmac('muko-contact-rate-limit', ip_address).hexdigest()
        key = f'contact-rate:{fingerprint}'
        limit = max(settings.CONTACT_RATE_LIMIT, 1)
        window = max(settings.CONTACT_RATE_LIMIT_WINDOW_SECONDS, 1)

        try:
            if cache.add(key, 1, timeout=window):
                return super().post(request, *args, **kwargs)
            attempts = cache.incr(key)
        except Exception:
            logger.exception('Contact rate limiter unavailable; allowing submission.')
            return super().post(request, *args, **kwargs)

        if attempts <= limit:
            return super().post(request, *args, **kwargs)

        form = self.get_form()
        form.add_error(None, 'Too many messages from this connection. Please try again later or use WhatsApp.')
        return TemplateResponse(request, self.template_name, {'form': form}, status=429)

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.ip_address = None
        submission.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        submission.save()

        try:
            send_mail(
                subject=f'New contact from {submission.name}',
                message=(
                    f'Name: {submission.name}\n'
                    f'Email: {submission.email}\n\n'
                    f'Message:\n{submission.message}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_NOTIFICATION_EMAIL],
                fail_silently=False,
            )
        except Exception:
            logger.exception('Contact notification email failed for submission %s.', submission.pk)

        return TemplateResponse(self.request, 'core/partials/contact_success.html')

    def form_invalid(self, form):
        return TemplateResponse(
            self.request, self.template_name, {'form': form}, status=422
        )
