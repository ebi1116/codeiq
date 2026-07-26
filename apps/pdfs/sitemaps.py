from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import InterviewPDF


class PDFSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return InterviewPDF.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ["core:home", "core:pricing", "core:faq", "core:about", "core:contact", "pdfs:pdf_list"]

    def location(self, item):
        return reverse(item)
