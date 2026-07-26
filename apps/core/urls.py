from django.contrib.sitemaps.views import sitemap
from django.urls import path

from apps.pdfs.sitemaps import PDFSitemap, StaticViewSitemap
from . import views

app_name = "core"

sitemaps = {"pdfs": PDFSitemap, "static": StaticViewSitemap}

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("pricing/", views.PricingView.as_view(), name="pricing"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-and-conditions/", views.TermsView.as_view(), name="terms"),
    path("refund-cancellation-policy/", views.RefundPolicyView.as_view(), name="refund_policy"),
    path("shipping-delivery-policy/", views.ShippingPolicyView.as_view(), name="shipping_policy"),
    path("disclaimer/", views.DisclaimerView.as_view(), name="disclaimer"),
    path("cookie-policy/", views.CookiePolicyView.as_view(), name="cookie_policy"),
    path("copyright-policy/", views.CopyrightPolicyView.as_view(), name="copyright_policy"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
