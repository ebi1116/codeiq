from django.conf import settings


def site_settings(request):
    ctx = {
        "SITE_NAME": getattr(settings, "SITE_NAME", "CodeIQ"),
        "SITE_TAGLINE": getattr(settings, "SITE_TAGLINE", ""),
        "RAZORPAY_KEY_ID": getattr(settings, "RAZORPAY_KEY_ID", ""),
    }
    try:
        from apps.pdfs.models import Category, Technology
        ctx["NAV_CATEGORIES"] = Category.objects.filter(parent__isnull=True)[:12]
        ctx["NAV_TECHNOLOGIES"] = Technology.objects.all()[:12]
    except Exception:
        ctx["NAV_CATEGORIES"] = []
        ctx["NAV_TECHNOLOGIES"] = []
    return ctx
