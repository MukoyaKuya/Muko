from django.http import Http404
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

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
