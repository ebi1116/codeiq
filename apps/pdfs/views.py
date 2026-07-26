from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models.functions import Lower
from django.db.models import Case, IntegerField, Q, Value, When

from .models import InterviewPDF, Category, Technology, Company, LegacyCategoryTechnologyRedirect


class PDFListView(ListView):
    model = InterviewPDF
    template_name = "pdfs/pdf_list.html"
    context_object_name = "pdfs"
    paginate_by = 12

    def get_queryset(self):
        qs = InterviewPDF.objects.filter(is_published=True)
        pricing = self.request.GET.get("pricing")
        if pricing == "free":
            qs = qs.filter(is_free=True)
        elif pricing == "premium":
            qs = qs.filter(is_free=False)
        sort = self.request.GET.get("sort", "latest")
        if sort == "popular":
            qs = qs.order_by("-downloads_count")
        elif sort == "trending":
            qs = qs.order_by("-is_trending", "-views_count")
        else:
            qs = qs.order_by("-created_at")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["technologies"] = Technology.objects.all()
        ctx["companies"] = Company.objects.all()
        return ctx


class CategoryDetailView(ListView):
    template_name = "pdfs/category_detail.html"
    context_object_name = "pdfs"
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        if not Category.objects.filter(slug=slug).exists():
            legacy_redirect = LegacyCategoryTechnologyRedirect.objects.select_related("technology").filter(
                legacy_slug=slug
            ).first()
            if legacy_redirect:
                return redirect(legacy_redirect.technology.get_absolute_url(), permanent=True)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return InterviewPDF.objects.filter(is_published=True, category=self.category).select_related(
            "category", "technology", "company"
        ).order_by("display_order")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category"] = self.category
        technologies = Technology.objects.filter(
            Q(categories=self.category) | Q(category=self.category)
        ).distinct().order_by("order", "name")
        technology_names = technologies.annotate(normalized_name=Lower("name")).values("normalized_name")
        # Defensive rendering guard for old data: a nested category named after
        # a technology would otherwise produce two identical-looking cards.
        ctx["child_categories"] = self.category.children.annotate(
            normalized_name=Lower("name")
        ).exclude(normalized_name__in=technology_names)
        ctx["technologies"] = technologies
        return ctx


class TechnologyDetailView(ListView):
    template_name = "pdfs/technology_detail.html"
    context_object_name = "pdfs"
    paginate_by = 12

    def get_queryset(self):
        self.technology = get_object_or_404(Technology, slug=self.kwargs["slug"])
        content_order = Case(*[
            When(content_type=value, then=Value(position))
            for position, (value, label) in enumerate(InterviewPDF.ContentType.choices)
        ], output_field=IntegerField())
        return InterviewPDF.objects.filter(is_published=True, technology=self.technology).select_related(
            "category", "technology", "company"
        ).order_by(content_order, "display_order", "title")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["technology"] = self.technology
        return ctx


class CompanyDetailView(ListView):
    template_name = "pdfs/company_detail.html"
    context_object_name = "pdfs"
    paginate_by = 12

    def get_queryset(self):
        self.company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return InterviewPDF.objects.filter(is_published=True, company=self.company)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["company"] = self.company
        return ctx


class PDFDetailView(DetailView):
    model = InterviewPDF
    template_name = "pdfs/pdf_detail.html"
    context_object_name = "pdf"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return InterviewPDF.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pdf = self.object
        InterviewPDF.objects.filter(pk=pdf.pk).update(views_count=pdf.views_count + 1)

        user = self.request.user
        ctx["has_access"] = pdf.user_has_access(user)
        ctx["related_pdfs"] = InterviewPDF.objects.filter(
            is_published=True, category=pdf.category
        ).exclude(pk=pdf.pk)[:4]

        if user.is_authenticated:
            from apps.accounts.models import Wishlist, Bookmark, RecentlyViewed
            ctx["is_wishlisted"] = Wishlist.objects.filter(user=user, pdf=pdf).exists()
            ctx["is_bookmarked"] = Bookmark.objects.filter(user=user, pdf=pdf).exists()
            RecentlyViewed.objects.update_or_create(user=user, pdf=pdf)
        return ctx


def preview_pdf(request, slug):
    pdf = get_object_or_404(InterviewPDF, slug=slug, is_published=True)
    if not pdf.preview_pdf:
        raise Http404("No preview available for this PDF.")
    return FileResponse(pdf.preview_pdf.open("rb"), content_type="application/pdf")


@login_required
def download_pdf(request, slug):
    pdf = get_object_or_404(InterviewPDF, slug=slug, is_published=True)
    if not pdf.user_has_access(request.user):
        messages.error(request, "Please purchase this PDF to download it.")
        return redirect(pdf.get_absolute_url())

    from apps.accounts.models import DownloadHistory
    DownloadHistory.objects.create(user=request.user, pdf=pdf)
    InterviewPDF.objects.filter(pk=pdf.pk).update(downloads_count=pdf.downloads_count + 1)

    return FileResponse(
        (pdf.pdf_file or pdf.original_pdf).open("rb"),
        as_attachment=True,
        filename=f"{pdf.slug}.pdf",
        content_type="application/pdf",
    )


@login_required
def toggle_wishlist(request, slug):
    pdf = get_object_or_404(InterviewPDF, slug=slug)
    from apps.accounts.models import Wishlist
    obj, created = Wishlist.objects.get_or_create(user=request.user, pdf=pdf)
    if not created:
        obj.delete()
        wishlisted = False
    else:
        wishlisted = True
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"wishlisted": wishlisted})
    return redirect(pdf.get_absolute_url())


@login_required
def toggle_bookmark(request, slug):
    pdf = get_object_or_404(InterviewPDF, slug=slug)
    from apps.accounts.models import Bookmark
    obj, created = Bookmark.objects.get_or_create(user=request.user, pdf=pdf)
    if not created:
        obj.delete()
        bookmarked = False
    else:
        bookmarked = True
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"bookmarked": bookmarked})
    return redirect(pdf.get_absolute_url())
