# Muko

Muko is a small Django portfolio site with a server-rendered landing page, WhatsApp-first contact flow, admin-managed content, and environment-backed runtime settings.
 
## Stack 
     
- Python  
- Django 6.0.8  
- SQLite for local development
- HTMX on the contact form
- Locally compiled Tailwind CSS and pinned browser libraries 
 
## Local setup 
   
1. Install Python 3.13 from [python.org](https://www.python.org/downloads/) and ensure the Python Launcher (`py`) is available.
2. Create a clean virtual environment and install dependencies:

```bash
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
```

On PowerShell, `./scripts/bootstrap.ps1` performs the same setup. If an existing virtual environment points to a removed interpreter, run `./scripts/bootstrap.ps1 -RecreateVenv`.

3. Create a local environment file from the example:

```bash
copy .env.example .env
```

4. Keep development values in `.env`, for example:

```env
DJANGO_ENV=development
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

5. Apply migrations:

```bash
python manage.py migrate
```

6. Start the server:

```bash
python manage.py runserver
```

## Contact flow

- The primary contact CTA opens a WhatsApp conversation via a configurable `WHATSAPP_CONTACT_URL` env var.
- The homepage contact form posts to `/contact/` with HTMX and stores valid `ContactSubmission` records for admin review.
- The contact form includes a hidden honeypot field to reject simple bot submissions without adding friction for visitors.

## Production checklist

Set these values in `.env` or your hosting platform environment:

```env
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=replace-with-a-real-secret
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SITE_URL=https://your-domain.com
WHATSAPP_CONTACT_URL=https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.
CONTACT_RATE_LIMIT=5
CONTACT_RATE_LIMIT_WINDOW_SECONDS=3600
ANALYTICS_ENABLED=True
TRACK_BOT_VISITS=False
TRUST_GEO_HEADERS=False
# Optional local MaxMind GeoLite2-Country database, stored outside the web root.
# GEOIP_DATABASE_PATH=/home/your-cpanel-user/geoip/GeoLite2-Country.mmdb
VISITOR_LOG_RETENTION_DAYS=90
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
USE_X_FORWARDED_PROTO=True
SECURE_HSTS_SECONDS=63072000
# These are enabled by default in production. Confirm every subdomain supports HTTPS.
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

## Static files

Static collection is configured with `STATIC_ROOT=staticfiles` and uses hashed, compressed filenames. Build the local Tailwind stylesheet before collecting static files:

```bash
npm install
npm run build:css
python manage.py collectstatic --noinput
```

The compiled stylesheet and pinned browser libraries are committed under `static/`, so HostPinnacle deployments do not need Node.js if the tracked build output is current. Copy [deployment/hostpinnacle-static.htaccess](deployment/hostpinnacle-static.htaccess) to the deployed static directory as `.htaccess` to give LiteSpeed/Apache long-lived cache headers for fingerprinted assets.

For higher-traffic production environments, serve `staticfiles` and `media` through the host, reverse proxy, or CDN. In production Django intentionally does not serve `/media/`; configure HostPinnacle's web server with a `/media/` alias that points to `MEDIA_ROOT`.

## Analytics, privacy, and spam protection

- Visitor IP addresses are stored only as Django-keyed hashes. The application does not call external IP-geolocation services.
- Country reporting can use either `TRUST_GEO_HEADERS=True` behind a trusted CDN that supplies `CF-IPCountry`, or a local MaxMind GeoLite2-Country database. Set `GEOIP_DATABASE_PATH` to its absolute `.mmdb` path; the database stays outside the public web root and visitor IPs never leave the server. Update the GeoLite2 database monthly.
- Bots are excluded by default. Enable `TRACK_BOT_VISITS=True` only if crawler reporting is needed.
- Visitor event data must be pruned on a schedule. Configure this HostPinnacle cron job daily:

```bash
python /path/to/manage.py prune_visitor_logs
```

- The contact form uses a honeypot and a cache-backed per-IP rate limit. Sender IPs are not stored with contact submissions. Use a shared cache backend when running multiple application processes.

## Useful commands

```bash
python manage.py check
python manage.py test
python manage.py collectstatic --noinput
python manage.py prune_visitor_logs
python manage.py createsuperuser
```

## Notes

- The default local database is SQLite.
- Tailwind is compiled into `static/css/site.css`; Lucide, HTMX, and GSAP are pinned and served locally from `static/vendor/`. Google Fonts remain external.
- Production mode fails fast if `SECRET_KEY` is left at the development default or if `ALLOWED_HOSTS` is empty.
