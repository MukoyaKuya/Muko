import secrets
import time
from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .geoip import lookup_country_name
from .models import Visitor, VisitLog


class SecurityHeadersMiddleware:
    """Add public-site security headers without breaking Django's admin interface."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(18)
        response = self.get_response(request)

        response['Permissions-Policy'] = 'camera=(), geolocation=(), microphone=(), payment=(), usb=()'
        if request.path.startswith('/admin/'):
            return response

        nonce = request.csp_nonce
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            f"script-src 'self' 'nonce-{nonce}'; "
            "connect-src 'self'; "
            "upgrade-insecure-requests"
        )
        return response


class VisitorTrackingMiddleware:
    """Count privacy-preserving portfolio visits per hashed IP address."""

    EXCLUDED_PREFIXES = ('/admin/', '/static/', '/media/')
    EXCLUDED_PATHS = ('/favicon.ico', '/robots.txt')

    def __init__(self, get_response):
        self.get_response = get_response
        self.cooldown = getattr(settings, 'VISITOR_TRACKING_COOLDOWN_SECONDS', 1800)

    def __call__(self, request):
        response = self.get_response(request)

        if self._should_track(request, response):
            self._track(request)

        return response

    def _should_track(self, request, response):
        if request.method != 'GET' or response.status_code >= 400:
            return False

        path = request.path
        if path in self.EXCLUDED_PATHS or path.startswith(self.EXCLUDED_PREFIXES):
            return False

        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type:
            return False

        return True

    def _client_ip(self, request):
        if getattr(settings, 'TRUST_X_FORWARDED_FOR', False):
            forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if forwarded:
                return forwarded.split(',', 1)[0].strip()
        return request.META.get('REMOTE_ADDR', '').strip()

    def _get_device_type(self, user_agent):
        ua = user_agent.lower()
        bot_markers = ('bot', 'crawler', 'spider', 'slurp', 'preview', 'headless', 'python-requests', 'curl', 'wget')
        if any(marker in ua for marker in bot_markers):
            return 'Bot/Crawler'
        tablet_markers = ('ipad', 'tablet', 'playbook', 'kindle', 'nexus 7', 'nexus 10')
        if any(marker in ua for marker in tablet_markers):
            return 'Tablet'
        mobile_markers = ('mobi', 'iphone', 'android', 'iemobile', 'phone', 'ipod')
        if any(marker in ua for marker in mobile_markers):
            return 'Mobile'
        return 'Desktop'

    def _get_region(self, request, ip):
        if ip in ('127.0.0.1', 'localhost', '::1') or ip.startswith(('192.168.', '10.', '172.16.')):
            return 'Local'
        if getattr(settings, 'TRUST_GEO_HEADERS', False):
            country = request.META.get('HTTP_CF_IPCOUNTRY', '').upper()
            if len(country) == 2 and country not in {'XX', 'T1'}:
                return country
        country = lookup_country_name(ip)
        if country:
            return country
        return 'Unknown'

    def _track(self, request):
        if not getattr(settings, 'ANALYTICS_ENABLED', True):
            return

        ip_address = self._client_ip(request)
        if not ip_address:
            return

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        device_type = self._get_device_type(user_agent)
        is_bot = (device_type == 'Bot/Crawler')
        if is_bot and not getattr(settings, 'TRACK_BOT_VISITS', False):
            return

        ip_hash = salted_hmac('muko-visitor-ip', ip_address).hexdigest()
        now = timezone.now()

        visitor = Visitor.objects.filter(ip_hash=ip_hash).first()
        if visitor:
            now_ts = int(time.time())
            last_tracked_session = request.session.get('visitor_last_tracked_at', 0)
            if is_bot:
                # Bots don't support sessions. Check cooldown against DB last_seen.
                if now - visitor.last_seen < timedelta(seconds=self.cooldown):
                    return
            else:
                # Real users support sessions. Use session-based cooldown.
                if now_ts - last_tracked_session < self.cooldown:
                    return

        if not visitor:
            defaults = {
                'visit_count': 1,
                'last_seen': now,
                'last_path': request.path[:255],
                'user_agent': user_agent[:500],
                'device_type': device_type,
                'region': self._get_region(request, ip_address),
                'is_bot': is_bot,
            }
            try:
                visitor, created = Visitor.objects.get_or_create(
                    ip_hash=ip_hash,
                    defaults=defaults,
                )
            except IntegrityError:
                visitor = Visitor.objects.get(ip_hash=ip_hash)
                created = False
        else:
            created = False

        if not created:
            updates = {
                'visit_count': F('visit_count') + 1,
                'last_seen': now,
                'last_path': request.path[:255],
                'user_agent': user_agent[:500],
                'device_type': device_type,
                'is_bot': is_bot,
            }
            # Older records created before local GeoLite2 was configured can be
            # enriched when the same visitor returns, without retaining a raw IP.
            if visitor.region in {'', 'Unknown'}:
                updates['region'] = self._get_region(request, ip_address)

            Visitor.objects.filter(pk=visitor.pk).update(
                **updates,
            )

        # Log the visit event
        VisitLog.objects.create(
            visitor=visitor,
            timestamp=now,
            path=request.path[:255],
            is_bot=is_bot,
        )

        request.session['visitor_last_tracked_at'] = int(time.time())
