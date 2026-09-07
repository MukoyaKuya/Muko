"""Print the local GeoLite2 configuration and a known-country lookup.

Run this file directly from cPanel's Python App "Execute python script" field.
It does not write to the database or change any application data.
"""

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.utils import timezone  # noqa: E402
from core.geoip import lookup_country_name  # noqa: E402
from core.middleware import VisitorTrackingMiddleware  # noqa: E402
from core.models import Visitor  # noqa: E402


print(f'GEOIP_DATABASE_PATH={settings.GEOIP_DATABASE_PATH}')
database_path = Path(settings.GEOIP_DATABASE_PATH)
print(f'Database file exists={database_path.is_file()}')

try:
    from geoip2.database import Reader

    with Reader(str(database_path)) as reader:
        country = reader.country('8.8.8.8').country
    print(f'Direct GeoLite2 lookup for 8.8.8.8={country.name or country.iso_code}')
except Exception as exc:
    print(f'Direct GeoLite2 error={type(exc).__name__}: {exc}')

print(f'GeoLite2 lookup for 8.8.8.8={lookup_country_name("8.8.8.8")}')
middleware = VisitorTrackingMiddleware(lambda request: None)
print(f'Middleware country lookup for 8.8.8.8={middleware._get_region(None, "8.8.8.8")}')
print(f'ANALYTICS_ENABLED={settings.ANALYTICS_ENABLED}')
print(f'Django time={timezone.localtime().isoformat()} ({settings.TIME_ZONE})')

latest_visitor = Visitor.objects.order_by('-last_seen').first()
if latest_visitor:
    latest_seen = timezone.localtime(latest_visitor.last_seen)
    print(
        'Latest visitor='
        f'{latest_seen.isoformat()} '
        f'path={latest_visitor.last_path} region={latest_visitor.region}'
    )
else:
    print('Latest visitor=None')
