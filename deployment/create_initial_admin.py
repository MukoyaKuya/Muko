"""Create the first Django admin from cPanel environment variables, once."""

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.contrib.auth import get_user_model


username = os.environ.get("INITIAL_ADMIN_USERNAME", "").strip()
email = os.environ.get("INITIAL_ADMIN_EMAIL", "").strip()
password = os.environ.get("INITIAL_ADMIN_PASSWORD", "")

if not username or not email or not password:
    raise SystemExit(
        "Set INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_EMAIL, and "
        "INITIAL_ADMIN_PASSWORD in cPanel before running this script."
    )

User = get_user_model()
if User.objects.filter(username=username).exists():
    print(f"Admin user '{username}' already exists; no change made.")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Admin user '{username}' created successfully.")
