from django.db import migrations, models
import django.db.models.deletion


def remove_legacy_category_technology_duplicates(apps, schema_editor):
    Category = apps.get_model("pdfs", "Category")
    Technology = apps.get_model("pdfs", "Technology")
    Redirect = apps.get_model("pdfs", "LegacyCategoryTechnologyRedirect")

    # Only delete leaf categories with no PDFs. Their parent already displays
    # the canonical technology, and the redirect preserves their old URL.
    for category in Category.objects.exclude(parent__isnull=True).order_by("pk"):
        technology = Technology.objects.filter(
            categories=category.parent,
            name__iexact=category.name,
        ).first()
        if technology and not category.pdfs.exists() and not category.children.exists():
            Redirect.objects.get_or_create(
                legacy_slug=category.slug,
                defaults={"technology_id": technology.pk},
            )
            category.delete()


class Migration(migrations.Migration):
    dependencies = [("pdfs", "0004_dedupe_technology_names_and_constraint")]

    operations = [
        migrations.CreateModel(
            name="LegacyCategoryTechnologyRedirect",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("legacy_slug", models.SlugField(max_length=120, unique=True)),
                ("technology", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="legacy_category_redirects", to="pdfs.technology")),
            ],
            options={
                "verbose_name": "Legacy category technology redirect",
                "verbose_name_plural": "Legacy category technology redirects",
            },
        ),
        migrations.RunPython(remove_legacy_category_technology_duplicates, migrations.RunPython.noop),
    ]
