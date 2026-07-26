from django.db import migrations, models
from django.db.models.functions import Lower


def merge_case_duplicate_technologies(apps, schema_editor):
    """Merge legacy case variants without dropping PDF/category relationships."""
    Technology = apps.get_model("pdfs", "Technology")
    InterviewPDF = apps.get_model("pdfs", "InterviewPDF")

    groups = {}
    for technology in Technology.objects.all().order_by("order", "id"):
        groups.setdefault(technology.name.strip().casefold(), []).append(technology)

    for technologies in groups.values():
        if len(technologies) < 2:
            continue
        keeper = technologies[0]
        for duplicate in technologies[1:]:
            # Category membership is a separate relation, so adding it to the
            # keeper preserves all category cards before the duplicate is gone.
            keeper.categories.add(*duplicate.categories.all())
            InterviewPDF.objects.filter(technology_id=duplicate.pk).update(technology_id=keeper.pk)
            duplicate.delete()


class Migration(migrations.Migration):
    dependencies = [("pdfs", "0003_category_display_order_and_interviewpdf_ordering")]

    operations = [
        migrations.RunPython(merge_case_duplicate_technologies, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="technology",
            constraint=models.UniqueConstraint(Lower("name"), name="pdfs_technology_name_ci_unique"),
        ),
    ]
