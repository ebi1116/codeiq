import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.pdfs.models import Category, InterviewPDF, Technology


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class InterviewPDFAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="pdf-admin", email="admin@example.com", password="test-password"
        )
        self.client.force_login(self.admin_user)
        self.category = Category.objects.create(name="Admin Tests", display_order=9000)
        self.technology = Technology.objects.create(name="Admin Technology", category=self.category)
        self.technology.categories.add(self.category)

    @staticmethod
    def upload(name, content=b"test"):
        return SimpleUploadedFile(name, content, content_type="application/pdf")

    def form_data(self, **overrides):
        data = {
            "title": "Admin PDF",
            "slug": "admin-pdf",
            "description": "Editable description",
            "topics_covered": "Django",
            "display_order": 1,
            "category": self.category.pk,
            "technology": self.technology.pk,
            "content_type": InterviewPDF.ContentType.NOTES,
            "company": "",
            "experience": "junior",
            "difficulty": "intermediate",
            "language": "english",
            "pages": 10,
            "price": "99.00",
            "is_premium": "on",
            "status": InterviewPDF.Status.PUBLISHED,
            "seo_title": "Admin SEO",
            "seo_description": "SEO description",
            "seo_keywords": "django",
            "_save": "Save",
        }
        data.update(overrides)
        return data

    def test_admin_can_create_edit_and_delete_interview_pdf(self):
        create_data = self.form_data()
        create_data.update({
            "thumbnail": SimpleUploadedFile("thumb.gif", b"GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;", content_type="image/gif"),
            "pdf_file": self.upload("admin.pdf", b"%PDF-1.4 test"),
        })
        response = self.client.post("/admin/pdfs/interviewpdf/add/", create_data, secure=True)
        self.assertEqual(response.status_code, 302)
        pdf = InterviewPDF.objects.get(slug="admin-pdf")
        self.assertTrue(pdf.is_premium)
        self.assertFalse(pdf.is_free)
        self.assertEqual(pdf.content_type, InterviewPDF.ContentType.NOTES)

        change_url = f"/admin/pdfs/interviewpdf/{pdf.pk}/change/"
        self.assertEqual(self.client.get(change_url, secure=True).status_code, 200)
        response = self.client.post(change_url, self.form_data(title="Edited PDF"), secure=True)
        self.assertEqual(response.status_code, 302)
        pdf.refresh_from_db()
        self.assertEqual(pdf.title, "Edited PDF")
        self.assertTrue(pdf.pdf_file)

        delete_url = f"/admin/pdfs/interviewpdf/{pdf.pk}/delete/"
        self.assertEqual(self.client.get(delete_url, secure=True).status_code, 200)
        response = self.client.post(delete_url, {"post": "yes"}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(InterviewPDF.objects.filter(pk=pdf.pk).exists())
