from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404
from django.template.response import TemplateResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import ContactSubmissionForm
from .models import FeaturedProject, ShopItem, ShopSectionSettings

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
        context['shop_items'] = ShopItem.objects.filter(is_published=True)
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
        return context


class ContactView(FormView):
    form_class = ContactSubmissionForm
    template_name = 'core/partials/contact_form.html'

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.ip_address = self.request.META.get('REMOTE_ADDR')
        submission.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        submission.save()

        send_mail(
            subject=f'New contact from {submission.name}',
            message=(
                f'Name: {submission.name}\n'
                f'Email: {submission.email}\n'
                f'IP: {submission.ip_address}\n\n'
                f'Message:\n{submission.message}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_NOTIFICATION_EMAIL],
            fail_silently=True,
        )

        return TemplateResponse(self.request, 'core/partials/contact_success.html')

    def form_invalid(self, form):
        return TemplateResponse(
            self.request, self.template_name, {'form': form}, status=422
        )
