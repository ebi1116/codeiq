# Generated manually to preserve existing category and PDF data before constraints are applied.

from django.db import migrations, models


CANONICAL_CATEGORY_ORDER = ("Python", "Java", "JavaScript", "React", "Django", "AWS")


def populate_display_orders(apps, schema_editor):
    Category = apps.get_model("pdfs", "Category")
    InterviewPDF = apps.get_model("pdfs", "InterviewPDF")

    categories = list(Category.objects.order_by("order", "name", "pk"))
    canonical_positions = {name: position for position, name in enumerate(CANONICAL_CATEGORY_ORDER, start=1)}
    remaining_position = len(canonical_positions) + 1

    for category in categories:
        position = canonical_positions.get(category.name)
        if position is None:
            position = remaining_position
            remaining_position += 1
        Category.objects.filter(pk=category.pk).update(display_order=position)

    for category in Category.objects.order_by("pk"):
        for position, pdf in enumerate(
            InterviewPDF.objects.filter(category_id=category.pk).order_by("created_at", "pk"),
            start=1,
        ):
            InterviewPDF.objects.filter(pk=pdf.pk).update(
                display_order=position,
                is_premium=not pdf.is_free,
                pdf_file=pdf.original_pdf,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("pdfs", "0002_category_parent_technology_banner_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["display_order"], "verbose_name_plural": "Categories"},
        ),
        migrations.AlterModelOptions(
            name="interviewpdf",
            options={
                "ordering": ["category", "display_order"],
                "verbose_name": "Interview PDF",
                "verbose_name_plural": "Interview PDFs",
            },
        ),
        migrations.AddField(
            model_name="category",
            name="banner",
            field=models.ImageField(blank=True, null=True, upload_to="categories/banners/"),
        ),
        migrations.AddField(
            model_name="category",
            name="display_order",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="thumbnail",
            field=models.ImageField(blank=True, null=True, upload_to="categories/thumbnails/"),
        ),
        migrations.AddField(
            model_name="interviewpdf",
            name="display_order",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="interviewpdf",
            name="is_premium",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="interviewpdf",
            name="pdf_file",
            field=models.FileField(
                blank=True,
                help_text="Canonical PDF file. Existing records retain their original protected file.",
                upload_to="pdfs/files/",
            ),
        ),
        migrations.RunPython(populate_display_orders, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name="category",
            index=models.Index(fields=["display_order"], name="pdfs_cat_display_order_idx"),
        ),
        migrations.AddIndex(
            model_name="interviewpdf",
            index=models.Index(fields=["display_order"], name="pdfs_pdf_display_order_idx"),
        ),
        migrations.AddConstraint(
            model_name="interviewpdf",
            constraint=models.UniqueConstraint(
                fields=("category", "display_order"),
                name="pdfs_interview_unique_category_display_order",
            ),
        ),
    ]
