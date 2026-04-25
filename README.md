# Muko

Muko is a small Django portfolio site with a server-rendered landing page, WhatsApp-first contact flow, admin-managed content, and environment-backed runtime settings.

## Stack

- Python
- Django 6.0.4
- SQLite for local development
- HTMX on the contact form
- Tailwind CDN, GSAP, and Lucide loaded from external CDNs

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

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
- `ContactSubmission` records are available in the database and admin but are not wired to an active form endpoint.

## Production checklist

Set these values in `.env` or your hosting platform environment:

```env
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=replace-with-a-real-secret
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
WHATSAPP_CONTACT_URL=https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
USE_X_FORWARDED_PROTO=True
```

## Static files

Static collection is configured with `STATIC_ROOT=staticfiles` and `python manage.py collectstatic` succeeds with the current project settings.

WhiteNoise is configured in Django, so simpler deployments can serve collected static assets directly from the app process.

For higher-traffic production environments, it is still better to serve the contents of `staticfiles` from your platform, reverse proxy, or CDN layer.

## Useful commands

```bash
python manage.py check
python manage.py test
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Notes

- The default local database is SQLite.
- Frontend assets such as Tailwind, GSAP, Lucide (pinned to 1.11.0), and Google Fonts are currently loaded from third-party CDNs.
- Production mode fails fast if `SECRET_KEY` is left at the development default or if `ALLOWED_HOSTS` is empty.
