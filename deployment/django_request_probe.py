"""Temporary cPanel diagnostic: run the homepage through Django and print errors."""

import os
import sys
import traceback
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    import django

    django.setup()

    from django.conf import settings
    from django.test import Client

    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "mukoyakuya.online"]
    settings.DEBUG_PROPAGATE_EXCEPTIONS = True
    response = Client(raise_request_exception=True).get(
        "/",
        HTTP_HOST="mukoyakuya.online",
        HTTP_USER_AGENT="Googlebot",
        secure=True,
    )
    print(f"Homepage completed with HTTP {response.status_code}.")
except Exception:
    traceback.print_exc()
    raise
