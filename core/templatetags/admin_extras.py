import json
from datetime import timedelta

from django import template
from django.contrib.admin.models import LogEntry
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from core.models import ContactSubmission, FeaturedProject, ShopItem, ShopSectionSettings, Visitor, VisitLog

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

    # Privacy-preserving visitor analytics (Real users, exclude bots)
    unique_visitors = Visitor.objects.filter(is_bot=False).count()
    total_visits = Visitor.objects.filter(is_bot=False).aggregate(total=Sum('visit_count'))['total'] or 0
    visitors_today = Visitor.objects.filter(is_bot=False, last_seen__date=today).count()
    bot_hits_total = Visitor.objects.filter(is_bot=True).aggregate(total=Sum('visit_count'))['total'] or 0

    # Daily visitor logs (last 30 days, real visits vs bot hits)
    logs_qs = (
        VisitLog.objects
        .filter(timestamp__date__gte=start)
        .annotate(day=TruncDate('timestamp'))
        .values('day', 'is_bot')
        .annotate(n=Count('id'))
    )
    visits_map = {}
    bots_map = {}
    for row in logs_qs:
        day = row['day']
        if row['is_bot']:
            bots_map[day] = row['n']
        else:
            visits_map[day] = row['n']

    chart_visits = [visits_map.get(d, 0) for d in days]
    chart_bot_hits = [bots_map.get(d, 0) for d in days]

    # Device type breakdown
    device_qs = (
        Visitor.objects
        .values('device_type')
        .annotate(n=Count('id'))
    )
    device_counts = {row['device_type']: row['n'] for row in device_qs}
    device_labels = ['Desktop', 'Mobile', 'Tablet', 'Bot/Crawler']
    device_data = [device_counts.get(lbl, 0) for lbl in device_labels]

    # Top regions (exclude Local and Unknown)
    region_qs = (
        Visitor.objects
        .exclude(region__in=['Local', 'Unknown'])
        .values('region')
        .annotate(n=Count('id'))
        .order_by('-n')[:5]
    )
    top_regions = [{'name': r['region'], 'count': r['n']} for r in region_qs]

    # Content counts
    pub_projects = FeaturedProject.objects.filter(is_published=True).count()
    draft_projects = FeaturedProject.objects.filter(is_published=False).count()
    pub_shop = ShopItem.objects.filter(is_published=True).count()
    draft_shop = ShopItem.objects.filter(is_published=False).count()

    charts_dict = {
        'labels': labels,
        'activity': activity,
        'visits': chart_visits,
        'bot_hits': chart_bot_hits,
        'device_labels': device_labels,
        'device_data': device_data,
        'donut_labels': [
            'Published Projects', 'Draft Projects',
            'Published Shop', 'Draft Shop',
        ],
        'donut_data': [pub_projects, draft_projects, pub_shop, draft_shop],
    }

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
        'bot_hits_total': bot_hits_total,
        'top_regions': top_regions,
        # ``json_script`` in the admin template serialises this value safely.
        # Passing an already-serialised string here causes JSON to be encoded
        # twice, so Chart.js receives a string instead of the chart object.
        'charts_json': charts_dict,
        # Chart data (JSON strings for safe template output)
        'chart_labels': json.dumps(labels),
        'chart_activity': json.dumps(activity),
        'chart_visits': json.dumps(chart_visits),
        'chart_bot_hits': json.dumps(chart_bot_hits),
        'device_labels': json.dumps(device_labels),
        'device_data': json.dumps(device_data),
        'donut_labels': json.dumps([
            'Published Projects', 'Draft Projects',
            'Published Shop', 'Draft Shop',
        ]),
        'donut_data': json.dumps([pub_projects, draft_projects, pub_shop, draft_shop]),
    }
