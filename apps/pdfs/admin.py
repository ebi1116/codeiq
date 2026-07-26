from django.contrib import admin
from django.utils.html import format_html

from .forms import InterviewPDFAdminForm
from .models import Category, Technology, Company, InterviewPDF, LegacyCategoryTechnologyRedirect


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "parent", "slug", "icon", "technology_count", "pdf_count")
    list_editable = ("display_order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    list_filter = ("parent",)
    ordering = ("display_order",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("slug", "created_at", "updated_at")
        return ("created_at", "updated_at")

    def technology_count(self, obj):
        return obj.technologies.count()
    technology_count.short_description = "Technologies"

    def pdf_count(self, obj):
        return obj.pdfs.count()
    pdf_count.short_description = "PDFs"


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug", "icon", "order", "pdf_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description", "seo_keywords")
    list_filter = ("category",)
    ordering = ("order", "name")
    filter_horizontal = ("categories",)
    fieldsets = (
        ("Basic Info", {"fields": ("name", "slug", "category", "categories", "description", "icon", "order")}),
        ("Media", {"fields": ("logo", "banner")}),
        ("SEO", {"classes": ("collapse",), "fields": ("seo_title", "seo_description", "seo_keywords")}),
    )

    def pdf_count(self, obj):
        return obj.pdfs.count()
    pdf_count.short_description = "PDFs"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "pdf_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("order", "name")

    def pdf_count(self, obj):
        return obj.pdfs.count()
    pdf_count.short_description = "PDFs"


@admin.register(InterviewPDF)
class InterviewPDFAdmin(admin.ModelAdmin):
    form = InterviewPDFAdminForm
    list_display = (
        "thumb", "title", "category", "technology", "content_type", "company",
        "pages", "display_order", "pricing_badge", "is_premium", "status",
        "views_count", "downloads_count", "created_at",
    )
    list_editable = ("display_order",)
    list_display_links = ("thumb", "title")
    list_filter = (
        "category", "technology", "content_type", "company", "status",
        "experience", "is_premium", "created_at",
    )
    search_fields = ("title", "description", "seo_keywords")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views_count", "downloads_count", "created_at", "updated_at")
    list_per_page = 25

    fieldsets = (
        ("Classification", {
            "fields": ("category", "technology", "content_type")
        }),
        ("Basic Info", {
            "fields": ("title", "slug", "description", "topics_covered", "company", "experience", "pages", "display_order")
        }),
        ("Media Files", {
            "fields": ("thumbnail", "banner", "pdf_file")
        }),
        ("Pricing", {
            "fields": ("is_premium", "price")
        }),
        ("Publishing", {
            "fields": ("status",)
        }),
        ("SEO", {
            "classes": ("collapse",),
            "fields": ("seo_title", "seo_description")
        }),
        ("Stats", {
            "fields": ("views_count", "downloads_count", "created_at", "updated_at")
        }),
    )

    actions = ["make_featured", "make_trending", "publish", "unpublish"]

    def save_model(self, request, obj, form, change):
        # is_free is retained for storefront compatibility; the admin exposes
        # the clearer Premium Status control and keeps both flags consistent.
        obj.is_free = not obj.is_premium
        obj.is_published = obj.status == InterviewPDF.Status.PUBLISHED
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")

    def thumb(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', obj.thumbnail.url)
        return "-"
    thumb.short_description = "Thumb"

    def pricing_badge(self, obj):
        if obj.is_free:
            return format_html('<span style="color:#059669;font-weight:600;">{}</span>', "Free")
        return format_html('<span style="color:#2563EB;font-weight:600;">₹{}</span>', obj.price)
    pricing_badge.short_description = "Pricing"

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark selected as Featured"

    def make_trending(self, request, queryset):
        queryset.update(is_trending=True)
    make_trending.short_description = "Mark selected as Trending"

    def publish(self, request, queryset):
        queryset.update(is_published=True, status=InterviewPDF.Status.PUBLISHED)
    publish.short_description = "Publish selected"

    def unpublish(self, request, queryset):
        queryset.update(is_published=False, status=InterviewPDF.Status.DRAFT)
    unpublish.short_description = "Unpublish selected"
