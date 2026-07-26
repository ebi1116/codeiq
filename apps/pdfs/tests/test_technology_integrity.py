from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.pdfs.models import Category, LegacyCategoryTechnologyRedirect, Technology
from apps.pdfs.templatetags.technology_logos import LOGO_FILENAMES, technology_logo


class TechnologyIntegrityTests(TestCase):
    def setUp(self):
        self.python = Technology.objects.create(name="Python")

    def test_case_variants_are_rejected_by_model_validation(self):
        with self.assertRaises(ValidationError):
            Technology(name="python").full_clean()

    def test_case_variants_are_rejected_by_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Technology.objects.create(name="PYTHON")

    def test_every_logo_lookup_is_a_local_svg(self):
        # The template tag delegates URL hashing to the deployment manifest;
        # validate the resolver's local filename independently of that build.
        self.assertEqual(LOGO_FILENAMES["python"], "python")
        for filename in set(LOGO_FILENAMES.values()) | {"topic"}:
            self.assertTrue(
                (Path(settings.BASE_DIR) / "static" / "images" / "technology-logos" / f"{filename}.svg").exists(),
                f"Missing local logo asset: {filename}.svg",
            )

    def test_duplicate_legacy_category_card_is_not_rendered(self):
        parent = Category.objects.create(name="Languages", display_order=1)
        Category.objects.create(name="Python", slug="legacy-python", parent=parent, display_order=2)
        self.python.categories.add(parent)

        response = self.client.get(parent.get_absolute_url(), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="/category/legacy-python/"')

    def test_primary_category_membership_is_rendered_without_cross_category_leakage(self):
        languages = Category.objects.create(name="Languages", display_order=1)
        frontend = Category.objects.create(name="Frontend", display_order=2)
        self.python.category = languages
        self.python.save(update_fields=["category", "updated_at"])
        react = Technology.objects.create(name="React", category=frontend)

        response = self.client.get(languages.get_absolute_url(), secure=True)
        self.assertContains(response, self.python.get_absolute_url())
        self.assertNotContains(response, react.get_absolute_url())

    def test_removed_legacy_category_url_redirects_to_technology(self):
        LegacyCategoryTechnologyRedirect.objects.create(
            legacy_slug="legacy-python",
            technology=self.python,
        )

        response = self.client.get("/category/legacy-python/", secure=True)
        self.assertRedirects(
            response,
            self.python.get_absolute_url(),
            status_code=301,
            fetch_redirect_response=False,
        )
