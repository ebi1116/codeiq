from pathlib import Path

import requests
import urllib3
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.pdfs.templatetags.technology_logos import LOGO_FILENAMES


class Command(BaseCommand):
    help = "Download local Simple Icons SVGs used by technology cards. Safe to run repeatedly."

    def add_arguments(self, parser):
        parser.add_argument(
            "--insecure",
            action="store_true",
            help="Only for environments with an HTTPS-inspection certificate unavailable to Python.",
        )

    def handle(self, *args, **options):
        if options["insecure"]:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        target = Path(settings.BASE_DIR) / "static" / "images" / "technology-logos"
        target.mkdir(parents=True, exist_ok=True)
        downloaded = 0
        for slug in sorted(set(LOGO_FILENAMES.values())):
            destination = target / f"{slug}.svg"
            if destination.exists():
                continue
            response = requests.get(
                f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg",
                timeout=20,
                verify=not options["insecure"],
            )
            if response.status_code != 200 or not response.content.startswith(b"<svg"):
                raise CommandError(f"Could not download logo for {slug}.")
            destination.write_bytes(response.content)
            downloaded += 1
        self.stdout.write(self.style.SUCCESS(f"Technology logos ready ({downloaded} downloaded)."))
