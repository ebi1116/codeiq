# CodeIQ — Interview Questions PDF Platform

A production-ready Django platform where users discover, preview, purchase and download
interview-question PDFs by technology, company and role. Google-only auth, Razorpay
payments, glassmorphism dark/light UI.

## Tech Stack

- **Backend:** Python 3.12+, Django 6, Django REST Framework, SQLite (PostgreSQL-ready)
- **Auth:** django-allauth, Google OAuth only (no username/password signup)
- **Payments:** Razorpay
- **Frontend:** Bootstrap 5, vanilla JS, AOS, GSAP, Font Awesome, Google Font "Outfit"
- **Static/media:** WhiteNoise (static), local filesystem (media) — S3-ready for production

## Project Structure

```
codeiq/                 # Django project settings/urls
apps/
  core/                 # Home page, search, static pages, sitemap/robots
  accounts/             # Google-only auth adapters, dashboard, wishlist, bookmarks
  pdfs/                 # Category/Technology/Company/InterviewPDF models, admin, views
  orders/                # Razorpay checkout + payment verification + invoices
templates/              # All HTML templates (Bootstrap 5 + glassmorphism theme)
static/                 # style.css, main.js
media/                  # Uploaded thumbnails/banners/PDFs (created at runtime)
```

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   # source venv/bin/activate     # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in real values (Google OAuth keys, Razorpay
   keys, `SECRET_KEY`). The app runs fine locally with SQLite and empty payment/OAuth
   keys — those features will simply show a friendly message until configured.

3. **Run migrations and seed demo data**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed_demo_data --count 24
   ```

   `seed_demo_data` creates sample categories, technologies, companies and interview
   PDFs (with generated placeholder thumbnails and dummy PDF files) so the site isn't
   empty on first run. Replace these through the admin panel with real content whenever
   you're ready.

4. **Run the dev server**

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` for the site and `http://127.0.0.1:8000/admin/` for
   the admin panel.

## Google OAuth Setup

1. Go to [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials).
2. Create an **OAuth 2.0 Client ID** (Web application).
3. Add authorized redirect URI: `http://127.0.0.1:8000/accounts/google/login/callback/`
   (swap the domain for your production URL when you deploy).
4. Put the client ID / secret into `.env` as `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.
5. In `/admin/`, under **Sites**, make sure the one Site row matches your domain (or
   `127.0.0.1:8000` for local dev) — allauth reads the Google app config from settings
   automatically via `SOCIALACCOUNT_PROVIDERS`, no separate SocialApp DB row is needed.

There is no local signup/login page by design — "Continue with Google" is the only
entry point, exactly as specified.

## Razorpay Setup

1. Get **test mode** keys from the [Razorpay dashboard](https://dashboard.razorpay.com/app/keys).
2. Put them into `.env` as `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET`.
3. Until these are set, the "Purchase & Unlock" button will show a friendly warning
   instead of crashing — free PDFs work regardless.

## Managing Content

Everything is managed from `/admin/`:

- **Categories / Technologies / Companies** — simple name + slug + icon models.
- **Interview PDFs** — title, description, topics, classification, media files
  (thumbnail, banner, preview PDF, original PDF), pricing, and the Featured / Trending
  / Published toggles called for in the spec. SEO fields are in a collapsed fieldset.
- **Orders** — read-only Razorpay order/payment records with a status badge.

Free PDFs are downloadable by any signed-in user, unlimited times. Premium PDFs require
a `paid` Order record for that user before the secure download view will serve the file
— this is enforced in `InterviewPDF.user_has_access()`, not just hidden in the UI.

## Deployment Notes (AWS EC2 + Gunicorn + Nginx)

- Set `DEBUG=False` and a real `SECRET_KEY` / `ALLOWED_HOSTS` in `.env`.
- Switch `DB_ENGINE=postgres` and fill in the DB_* variables for production.
- Run `python manage.py collectstatic` — WhiteNoise serves the compressed output.
- Point Gunicorn at `codeiq.wsgi:application`; put Nginx in front for TLS and static
  file caching headers.
- Security headers (HSTS, secure cookies, SSL redirect) auto-enable when `DEBUG=False`.

## What's Deliberately Out of Scope

This build focuses on the PDF-download product exactly as specified — there's no video
course engine, no username/password auth, and no features outside the brief. Frontend
is intentionally the only layer meant for ongoing customization; models, URLs, views
and payment logic should not need structural changes for typical content updates.
