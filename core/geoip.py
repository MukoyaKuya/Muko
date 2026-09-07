"""Offline, privacy-preserving country lookups for visitor analytics."""

import ipaddress
import logging
from functools import lru_cache
from pathlib import Path

from django.conf import settings

try:
    from geoip2.database import Reader
    from geoip2.errors import AddressNotFoundError
except ImportError:  # Keeps the application usable until the optional package is installed.
    Reader = None

    class AddressNotFoundError(Exception):
        pass


logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def _get_reader(database_path):
    """Open and cache an explicitly configured local GeoLite2 database."""
    if not database_path or Reader is None:
        return None

    path = Path(database_path)
    if not path.is_file():
        logger.warning('GeoIP database is unavailable at %s.', path)
        return None

    try:
        return Reader(str(path))
    except Exception:
        logger.exception('Unable to open GeoIP database at %s.', path)
        return None


def lookup_country_name(ip):
    """Return a country name, or ``None`` when a lookup is unavailable."""
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return None

    reader = _get_reader(getattr(settings, 'GEOIP_DATABASE_PATH', ''))
    if reader is None:
        return None

    try:
        country = reader.country(ip).country
        return country.name or country.iso_code or None
    except AddressNotFoundError:
        return None
    except Exception:
        logger.exception('GeoIP country lookup failed.')
        return None
