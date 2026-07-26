from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.pdfs.models import Category, InterviewPDF, Technology


class ContentStructureTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Programming Languages", display_order=1)
        self.technology = Technology.objects.create(name="Python", category=self.category)
        self.technology.categories.add(self.category)

    def create_content(self, title, content_type, display_order=1):
        return InterviewPDF.objects.create(
            title=title,
            description=title,
            category=self.category,
            technology=self.technology,
            content_type=content_type,
            thumbnail="pdfs/thumbnails/test.jpg",
            original_pdf="pdfs/originals/test.pdf",
            display_order=display_order,
        )

    def test_technology_supports_multiple_content_types_and_repeated_display_orders(self):
        self.create_content("Python Interview Questions", InterviewPDF.ContentType.INTERVIEW_QUESTIONS)
        self.create_content("Python Beginner Notes", InterviewPDF.ContentType.NOTES)
        self.create_content("Python MCQ Set 1", InterviewPDF.ContentType.MCQS)
        self.assertEqual(InterviewPDF.objects.filter(technology=self.technology).count(), 3)

    def test_duplicate_classification_and_title_is_rejected(self):
        self.create_content("Python Notes", InterviewPDF.ContentType.NOTES)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_content("Python Notes", InterviewPDF.ContentType.NOTES, display_order=2)

    def test_same_title_can_exist_under_a_different_content_type(self):
        self.create_content("Python Guide", InterviewPDF.ContentType.NOTES)
        self.create_content("Python Guide", InterviewPDF.ContentType.OTHER)
        self.assertEqual(InterviewPDF.objects.filter(title="Python Guide").count(), 2)

    def test_technology_page_groups_published_content_by_type(self):
        self.create_content("Python Interview Questions", InterviewPDF.ContentType.INTERVIEW_QUESTIONS)
        self.create_content("Python Beginner Notes", InterviewPDF.ContentType.NOTES)
        response = self.client.get(self.technology.get_absolute_url(), secure=True)
        self.assertContains(response, "Interview Questions")
        self.assertContains(response, "Notes")
        self.assertContains(response, "Python Beginner Notes")
