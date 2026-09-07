from django.conf import settings

from .models import PortfolioSettings, SiteContentSettings


def contact_links(request):
    portfolio_settings = PortfolioSettings.objects.first()
    site_content = SiteContentSettings.objects.first()

    # Get services (either from db or fallback to defaults)
    services = []
    services_js_data = {}

    if site_content and site_content.services.exists():
        for s in site_content.services.all():
            services.append(s)
            services_js_data[s.slug] = {
                'title': s.title,
                'icon': s.icon,
                'description': s.description,
                'includes': s.includes_list,
                'outcomes': s.outcomes_list,
            }
    else:
        # Static fallback data matching the original frontend
        default_services = [
            {
                'title': 'Web Development',
                'slug': 'web',
                'icon': 'code-2',
                'short_description': 'Fast, scalable applications built around real business goals.',
                'description': 'A complete path from a validated idea to a secure, maintainable web product—not just a collection of pages.',
                'includes_list': ['Discovery and technical planning', 'Responsive frontend implementation', 'Django, APIs and database architecture', 'Authentication, admin and integrations'],
                'outcomes_list': ['A production-ready application', 'Clean, maintainable source code', 'Deployment and handover documentation', 'A foundation that can scale'],
                'tags_list': [],
                'column_span': 2,
                'show_bg_icon': True,
                'icon_size_class': 'h-10 w-10',
                'max_width_class': 'max-w-sm',
                'layout_class': 'block text-left',
            },
            {
                'title': 'UI/UX Design',
                'slug': 'design',
                'icon': 'pen-tool',
                'short_description': 'Clear, intuitive interfaces designed around how people behave.',
                'description': 'Interfaces shaped around user needs, business priorities and a visual system that stays coherent as the product grows.',
                'includes_list': ['User flows and information architecture', 'Wireframes and interactive prototypes', 'High-fidelity responsive UI', 'Reusable design system foundations'],
                'outcomes_list': ['Clearer customer journeys', 'Faster development decisions', 'Consistent visual language', 'Designs ready for implementation'],
                'tags_list': [],
                'column_span': 2,
                'show_bg_icon': False,
                'icon_size_class': 'h-9 w-9',
                'max_width_class': '',
                'layout_class': 'block text-left',
            },
            {
                'title': 'Digital Platforms',
                'slug': 'platforms',
                'icon': 'layout-grid',
                'short_description': 'Connected digital systems that help organizations operate and grow.',
                'description': 'End-to-end platforms that connect content, operations and customer experiences into one dependable system.',
                'includes_list': ['Requirements and workflow mapping', 'CMS, portal or marketplace architecture', 'Third-party API integrations', 'Roles, permissions and reporting'],
                'outcomes_list': ['Less manual operational work', 'One reliable source of truth', 'Better customer self-service', 'A platform built for expansion'],
                'tags_list': [],
                'column_span': 2,
                'show_bg_icon': False,
                'icon_size_class': 'h-9 w-9',
                'max_width_class': '',
                'layout_class': 'block text-left',
            },
            {
                'title': 'Cloud Infrastructure',
                'slug': 'cloud',
                'icon': 'cloud',
                'short_description': 'Secure, observable environments built to deploy reliably and scale safely.',
                'description': 'Practical cloud foundations that keep applications deployable, observable and resilient without unnecessary complexity.',
                'includes_list': ['Environment and deployment architecture', 'CI/CD pipeline configuration', 'Security, backups and access controls', 'Monitoring and performance baselines'],
                'outcomes_list': ['Repeatable deployments', 'Reduced downtime risk', 'Clear operational visibility', 'Infrastructure ready to scale'],
                'tags_list': ['AWS', 'Azure'],
                'column_span': 3,
                'show_bg_icon': False,
                'icon_size_class': 'h-10 w-10',
                'max_width_class': 'max-w-md',
                'layout_class': 'flex h-full flex-col justify-between gap-5 text-left md:flex-row md:items-end',
            },
            {
                'title': 'Performance & SEO',
                'slug': 'seo',
                'icon': 'search',
                'short_description': 'Technical improvements that make your site faster, easier to find, and easier to use.',
                'description': 'Technical and content-focused improvements that help real people—and search engines—reach and use your site effectively.',
                'includes_list': ['Core Web Vitals and speed audit', 'Technical SEO and crawl review', 'Metadata and structured content', 'Accessibility and conversion checks'],
                'outcomes_list': ['Faster page experiences', 'Improved search visibility', 'Lower user drop-off', 'A prioritized optimization roadmap'],
                'tags_list': [],
                'column_span': 3,
                'show_bg_icon': False,
                'icon_size_class': 'h-9 w-9',
                'max_width_class': 'max-w-xl',
                'layout_class': 'block text-left',
            },
        ]
        services = default_services
        for s in default_services:
            services_js_data[s['slug']] = {
                'title': s['title'],
                'icon': s['icon'],
                'description': s['description'],
                'includes': s['includes_list'],
                'outcomes': s['outcomes_list'],
            }

    return {
        'whatsapp_contact_url': settings.WHATSAPP_CONTACT_URL,
        'whatsapp_phone_display': settings.WHATSAPP_PHONE_DISPLAY,
        'portfolio_cv_url': portfolio_settings.cv_file.url if portfolio_settings and portfolio_settings.cv_file else '',
        'portfolio_cv_label': portfolio_settings.cv_label if portfolio_settings else 'View CV',
        'site_content': site_content,
        'site_url': settings.SITE_URL,
        'default_meta_description': settings.DEFAULT_META_DESCRIPTION,
        'services': services,
        # ``json_script`` in the template serializes this value safely.  Passing
        # an already-serialized JSON string here would make the browser parse
        # it into a string instead of the service-details object.
        'services_json': services_js_data,
    }
