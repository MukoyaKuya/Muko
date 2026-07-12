import time

from django.conf import settings
from django.db import IntegrityError
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import Visitor


class VisitorTrackingMiddleware:
    """Count privacy-preserving portfolio visits per hashed IP address."""

    EXCLUDED_PREFIXES = ('/admin/', '/static/', '/media/')
    EXCLUDED_PATHS = ('/favicon.ico', '/robots.txt')
    BOT_MARKERS = ('bot', 'crawler', 'spider', 'slurp', 'preview', 'headless')

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

        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        return not any(marker in user_agent for marker in self.BOT_MARKERS)

    def _client_ip(self, request):
        if getattr(settings, 'TRUST_X_FORWARDED_FOR', False):
            forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if forwarded:
                return forwarded.split(',', 1)[0].strip()
        return request.META.get('REMOTE_ADDR', '').strip()

    def _track(self, request):
        ip_address = self._client_ip(request)
        if not ip_address:
            return

        now_ts = int(time.time())
        last_tracked = request.session.get('visitor_last_tracked_at', 0)
        if now_ts - last_tracked < self.cooldown:
            return

        ip_hash = salted_hmac('muko-visitor-ip', ip_address).hexdigest()
        now = timezone.now()
        defaults = {
            'visit_count': 1,
            'last_seen': now,
            'last_path': request.path[:255],
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
        }

        try:
            visitor, created = Visitor.objects.get_or_create(
                ip_hash=ip_hash,
                defaults=defaults,
            )
        except IntegrityError:
            visitor = Visitor.objects.get(ip_hash=ip_hash)
            created = False

        if not created:
            Visitor.objects.filter(pk=visitor.pk).update(
                visit_count=F('visit_count') + 1,
                last_seen=now,
                last_path=request.path[:255],
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )

        request.session['visitor_last_tracked_at'] = now_ts
