import json
from datetime import timedelta

from django import template
from django.contrib.admin.models import LogEntry
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from core.models import ContactSubmission, FeaturedProject, ShopItem, ShopSectionSettings, Visitor

register = template.Library()


@register.simple_tag
def admin_analytics_data():
    now = timezone.now()
    today = now.date()
    start = today - timedelta(days=29)
    days = [start + timedelta(days=i) for i in range(30)]

    # Admin activity per day (last 30 days via LogEntry)
    activity_qs = (
        LogEntry.objects
        .filter(action_time__date__gte=start)
        .annotate(day=TruncDate('action_time'))
        .values('day')
        .annotate(n=Count('id'))
        .order_by('day')
    )
    activity_map = {row['day']: row['n'] for row in activity_qs}
    labels = [d.strftime('%b %d') for d in days]
    activity = [activity_map.get(d, 0) for d in days]

    # Privacy-preserving visitor analytics
    unique_visitors = Visitor.objects.count()
    total_visits = Visitor.objects.aggregate(total=Sum('visit_count'))['total'] or 0
    visitors_today = Visitor.objects.filter(last_seen__date=today).count()
    # Content counts
    pub_projects = FeaturedProject.objects.filter(is_published=True).count()
    draft_projects = FeaturedProject.objects.filter(is_published=False).count()
    pub_shop = ShopItem.objects.filter(is_published=True).count()
    draft_shop = ShopItem.objects.filter(is_published=False).count()

    return {
        'published_projects': pub_projects,
        'draft_projects': draft_projects,
        'total_projects': pub_projects + draft_projects,
        'published_shop': pub_shop,
        'draft_shop': draft_shop,
        'total_shop': pub_shop + draft_shop,
        'shop_sections': ShopSectionSettings.objects.count(),
        'submissions': ContactSubmission.objects.count(),
        'unique_visitors': unique_visitors,
        'total_visits': total_visits,
        'visitors_today': visitors_today,
        # Chart data (JSON strings for safe template output)
        'chart_labels': json.dumps(labels),
        'chart_activity': json.dumps(activity),
        'donut_labels': json.dumps([
            'Published Projects', 'Draft Projects',
            'Published Shop', 'Draft Shop',
        ]),
        'donut_data': json.dumps([pub_projects, draft_projects, pub_shop, draft_shop]),
    }