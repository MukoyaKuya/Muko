from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import VisitLog


class Command(BaseCommand):
    help = 'Delete visitor event records older than the configured retention period.'

    def handle(self, *args, **options):
        retention_days = max(settings.VISITOR_LOG_RETENTION_DAYS, 1)
        cutoff = timezone.now() - timedelta(days=retention_days)
        deleted, _ = VisitLog.objects.filter(timestamp__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f'Deleted {deleted} visitor-log records older than {retention_days} days.'
            )
        )
