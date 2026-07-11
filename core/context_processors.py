from django.conf import settings


def contact_links(request):
    return {
        'whatsapp_contact_url': settings.WHATSAPP_CONTACT_URL,
        'whatsapp_phone_display': settings.WHATSAPP_PHONE_DISPLAY,
    }