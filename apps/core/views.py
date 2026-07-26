from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView

from apps.pdfs.models import Category, Technology, Company, InterviewPDF


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        published = InterviewPDF.objects.filter(is_published=True)
        # The home page is intentionally a category/technology discovery page.
        # PDF records remain available through their dedicated pages.
        ctx["categories"] = Category.objects.filter(parent__isnull=True).order_by("display_order")
        ctx["technologies"] = Technology.objects.all()[:16]
        ctx["stats"] = {
            "total_pdfs": published.count(),
            "total_categories": Category.objects.count(),
            "total_companies": Company.objects.count(),
            "total_downloads": sum(published.values_list("downloads_count", flat=True)),
        }
        return ctx


class SearchView(ListView):
    template_name = "core/search_results.html"
    context_object_name = "results"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        qs = InterviewPDF.objects.filter(is_published=True)
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
                | Q(technology__name__icontains=query)
                | Q(company__name__icontains=query)
                | Q(seo_keywords__icontains=query)
            ).distinct()
        experience = self.request.GET.get("experience")
        difficulty = self.request.GET.get("difficulty")
        pricing = self.request.GET.get("pricing")
        if experience:
            qs = qs.filter(experience=experience)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if pricing == "free":
            qs = qs.filter(is_free=True)
        elif pricing == "premium":
            qs = qs.filter(is_free=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        ctx["query"] = query
        ctx["technology_results"] = Technology.objects.none()
        ctx["category_results"] = Category.objects.none()
        if query:
            ctx["technology_results"] = (
                Technology.objects.filter(
                    Q(name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(seo_title__icontains=query)
                    | Q(seo_description__icontains=query)
                    | Q(seo_keywords__icontains=query)
                )
                .select_related("category")
                .order_by("order", "name")
            )
            ctx["category_results"] = Category.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).order_by("display_order", "name")
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"


class PricingView(TemplateView):
    template_name = "core/pricing.html"


class FAQView(TemplateView):
    template_name = "core/faq.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"


class PrivacyPolicyView(TemplateView):
    template_name = "core/privacy_policy.html"


class TermsView(TemplateView):
    template_name = "core/terms.html"


class RefundPolicyView(TemplateView):
    template_name = "core/refund_policy.html"


class ShippingPolicyView(TemplateView):
    template_name = "core/shipping_policy.html"


class DisclaimerView(TemplateView):
    template_name = "core/disclaimer.html"


class CookiePolicyView(TemplateView):
    template_name = "core/cookie_policy.html"


class CopyrightPolicyView(TemplateView):
    template_name = "core/copyright_policy.html"


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /dashboard/",
        "Disallow: /admin/",
        "Disallow: /orders/",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
