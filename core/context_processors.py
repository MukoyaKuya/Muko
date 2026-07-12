from django.conf import settings

from .models import PortfolioSettings, SiteContentSettings


def contact_links(request):
    portfolio_settings = PortfolioSettings.objects.first()
    site_content = SiteContentSettings.objects.first()
    return {
        'whatsapp_contact_url': settings.WHATSAPP_CONTACT_URL,
        'whatsapp_phone_display': settings.WHATSAPP_PHONE_DISPLAY,
        'portfolio_cv_url': portfolio_settings.cv_file.url if portfolio_settings and portfolio_settings.cv_file else '',
        'portfolio_cv_label': portfolio_settings.cv_label if portfolio_settings else 'View CV',
        'site_content': site_content,
    }