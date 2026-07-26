from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=60, blank=True, help_text="Font Awesome icon class, e.g. fa-brands fa-python")
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="categories/thumbnails/", blank=True, null=True)
    banner = models.ImageField(upload_to="categories/banners/", blank=True, null=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", blank=True, null=True,
        help_text="Optional parent for nested category groups such as Web Development > Frontend.",
    )
    order = models.PositiveIntegerField(default=0)
    display_order = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["display_order"]
        indexes = [
            models.Index(fields=["display_order"], name="pdfs_cat_display_order_idx"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pdfs:category_detail", kwargs={"slug": self.slug})


class Technology(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=60, blank=True)
    logo = models.ImageField(upload_to="technologies/", blank=True, null=True)
    banner = models.ImageField(upload_to="technologies/banners/", blank=True, null=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="primary_technologies", blank=True, null=True,
        help_text="Optional primary category used for organization in Django Admin.",
    )
    categories = models.ManyToManyField(
        Category, related_name="technologies", blank=True,
        help_text="Every category where this technology should be displayed.",
    )
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    seo_keywords = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Technologies"
        ordering = ["order", "name"]
        constraints = [
            # Technologies are shared between categories.  Making the canonical
            # record unique globally also guarantees a category can never render
            # two case variants of the same technology.
            models.UniqueConstraint(Lower("name"), name="pdfs_technology_name_ci_unique"),
        ]

    def clean(self):
        super().clean()
        normalized_name = (self.name or "").strip()
        if not normalized_name:
            return
        if type(self).objects.filter(name__iexact=normalized_name).exclude(pk=self.pk).exists():
            raise ValidationError({"name": "A technology with this name already exists (case-insensitive)."})

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        if not self.slug:
            base_slug = slugify(self.name) or "technology"
            slug = base_slug
            counter = 1
            while Technology.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pdfs:technology_detail", kwargs={"slug": self.slug})


class LegacyCategoryTechnologyRedirect(models.Model):
    """Keeps old category URLs working after a legacy technology-category is merged."""

    legacy_slug = models.SlugField(max_length=120, unique=True)
    technology = models.ForeignKey(Technology, on_delete=models.PROTECT, related_name="legacy_category_redirects")

    class Meta:
        verbose_name = "Legacy category technology redirect"
        verbose_name_plural = "Legacy category technology redirects"


class Company(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to="companies/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pdfs:company_detail", kwargs={"slug": self.slug})


class InterviewPDF(TimeStampedModel):
    class ContentType(models.TextChoices):
        INTERVIEW_QUESTIONS = "interview_questions", "Interview Questions"
        NOTES = "notes", "Notes"
        CHEAT_SHEET = "cheat_sheet", "Cheat Sheet"
        PROJECTS = "projects", "Projects"
        MCQS = "mcqs", "MCQs"
        ROADMAP = "roadmap", "Roadmaps"
        COMPANY_QUESTIONS = "company_questions", "Company Questions"
        INTERVIEW_EXPERIENCE = "interview_experience", "Interview Experience"
        TUTORIAL = "tutorial", "Tutorials"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    EXPERIENCE_CHOICES = [
        ("fresher", "Fresher (0-1 yrs)"),
        ("junior", "Junior (1-3 yrs)"),
        ("mid", "Mid (3-6 yrs)"),
        ("senior", "Senior (6+ yrs)"),
    ]
    LANGUAGE_CHOICES = [
        ("english", "English"),
        ("tamil", "Tamil"),
        ("hindi", "Hindi"),
    ]

    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=30, choices=ContentType.choices, default=ContentType.INTERVIEW_QUESTIONS, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    topics_covered = models.TextField(help_text="One topic per line", blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="pdfs")
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="pdfs", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name="pdfs", blank=True, null=True)

    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True, default="")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default="english")
    pages = models.PositiveIntegerField(default=1)

    thumbnail = models.ImageField(upload_to="pdfs/thumbnails/")
    banner = models.ImageField(upload_to="pdfs/banners/", blank=True, null=True)
    preview_pdf = models.FileField(upload_to="pdfs/previews/", blank=True, null=True,
                                    help_text="A short free preview/sample shown to everyone")
    original_pdf = models.FileField(upload_to="pdfs/originals/",
                                     help_text="The full, secure file only served through the protected download view")
    pdf_file = models.FileField(
        upload_to="pdfs/files/",
        blank=True,
        help_text="Canonical PDF file. Existing records retain their original protected file.",
    )

    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField()

    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PUBLISHED, db_index=True)

    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)

    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    seo_keywords = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Content Library item"
        verbose_name_plural = "Content Library"
        ordering = ["category", "technology", "content_type", "display_order", "title"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["display_order"], name="pdfs_pdf_display_order_idx"),
            models.Index(fields=["is_published", "is_featured"]),
            models.Index(fields=["is_published", "is_trending"]),
            models.Index(
                fields=["technology", "status", "content_type", "display_order"],
                name="pdfs_tech_content_order_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "technology", "content_type", "title"],
                name="pdfs_content_unique_category_technology_type_title",
            ),
        ]

    def clean(self):
        super().clean()
        if self.category_id and self.technology_id:
            if not self.technology.categories.filter(pk=self.category_id).exists() and self.technology.category_id != self.category_id:
                raise ValidationError({"technology": "Select a technology that belongs to the chosen category."})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while InterviewPDF.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        self.is_free = not self.is_premium
        self.is_published = self.status == self.Status.PUBLISHED
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("pdfs:pdf_detail", kwargs={"slug": self.slug})

    @property
    def topics_list(self):
        return [t.strip() for t in self.topics_covered.splitlines() if t.strip()]

    def user_has_access(self, user):
        """Free PDFs are open to everyone; premium PDFs require a completed order."""
        if self.is_free:
            return True
        if not user or not user.is_authenticated:
            return False
        return self.orders.filter(user=user, status="paid").exists()
