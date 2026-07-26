from django.db import migrations, models


def map_legacy_ebook(apps, schema_editor):
    InterviewPDF = apps.get_model("pdfs", "InterviewPDF")
    InterviewPDF.objects.filter(content_type="ebook").update(content_type="other")


class Migration(migrations.Migration):
    dependencies = [("pdfs", "0007_interviewpdf_pdfs_tech_content_order_idx")]

    operations = [
        migrations.RunPython(map_legacy_ebook, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="interviewpdf",
            options={"ordering": ["category", "technology", "content_type", "display_order", "title"], "verbose_name": "Content Library item", "verbose_name_plural": "Content Library"},
        ),
        migrations.AlterField(
            model_name="interviewpdf", name="content_type",
            field=models.CharField(choices=[("interview_questions", "Interview Questions"), ("notes", "Notes"), ("cheat_sheet", "Cheat Sheet"), ("projects", "Projects"), ("mcqs", "MCQs"), ("roadmap", "Roadmaps"), ("company_questions", "Company Questions"), ("interview_experience", "Interview Experience"), ("tutorial", "Tutorials"), ("other", "Other")], db_index=True, default="interview_questions", max_length=30),
        ),
        migrations.AlterField(
            model_name="interviewpdf", name="experience",
            field=models.CharField(blank=True, choices=[("fresher", "Fresher (0-1 yrs)"), ("junior", "Junior (1-3 yrs)"), ("mid", "Mid (3-6 yrs)"), ("senior", "Senior (6+ yrs)")], default="", max_length=20),
        ),
    ]
