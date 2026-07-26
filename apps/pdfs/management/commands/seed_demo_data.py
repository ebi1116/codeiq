import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.pdfs.models import Category, Technology, Company, InterviewPDF


CATEGORIES = [
    ("Python", "fa-python"), ("Java", "fa-java"), ("JavaScript", "fa-js"),
    ("SQL", "fa-database"), ("React", "fa-react"), ("Django", "fa-server"),
    ("AWS", "fa-aws"), ("DevOps", "fa-gears"), ("Docker", "fa-docker"),
    ("AI & ML", "fa-brain"), ("Data Science", "fa-chart-line"), ("HR Questions", "fa-comments"),
]

TECHNOLOGIES = ["Python", "Django", "React", "Node.js", "AWS", "Docker", "Kubernetes", "PostgreSQL"]

COMPANIES = ["TCS", "Infosys", "Wipro", "Accenture", "Amazon", "Google", "Microsoft", "Flipkart"]


def make_placeholder_image(text, size=(600, 450), bg=(37, 99, 235)):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size[0], size[1]], fill=bg)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((20, size[1] // 2 - 10), text[:40], fill=(255, 255, 255), font=font)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return ContentFile(buf.getvalue())


def make_placeholder_pdf(title):
    content = f"%PDF-1.4\n% Placeholder PDF for {title}\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>".encode()
    return ContentFile(content)


class Command(BaseCommand):
    help = "Seed the database with demo categories, technologies, companies and sample interview PDFs."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=24, help="Number of sample PDFs to create")

    def handle(self, *args, **options):
        random.seed(42)
        categories = []
        for i, (name, icon) in enumerate(CATEGORIES):
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"icon": icon, "order": i, "display_order": i + 1},
            )
            categories.append(cat)

        technologies = []
        for i, name in enumerate(TECHNOLOGIES):
            tech, _ = Technology.objects.get_or_create(name=name, defaults={"order": i})
            technologies.append(tech)

        companies = []
        for i, name in enumerate(COMPANIES):
            comp, _ = Company.objects.get_or_create(name=name, defaults={"order": i})
            companies.append(comp)

        count = options["count"]
        created = 0
        for i in range(count):
            cat = random.choice(categories)
            tech = random.choice(technologies)
            company = random.choice(companies) if random.random() > 0.3 else None
            is_free = random.random() > 0.55
            title = f"{cat.name} Interview Questions {'— ' + company.name if company else ''} #{i+1}".strip()

            if InterviewPDF.objects.filter(title=title).exists():
                continue

            pdf = InterviewPDF(
                title=title,
                description=(
                    f"A focused set of {cat.name} interview questions covering core concepts, "
                    f"practical scenarios and commonly asked follow-ups. Ideal for candidates "
                    f"preparing for {company.name if company else 'top tech'} interviews."
                ),
                topics_covered="\n".join([
                    f"{cat.name} Fundamentals", "Common Pitfalls", "Real Interview Scenarios",
                    "Coding Challenges", "Best Practices",
                ]),
                category=cat,
                technology=tech,
                company=company,
                experience=random.choice(["fresher", "junior", "mid", "senior"]),
                difficulty=random.choice(["beginner", "intermediate", "advanced"]),
                pages=random.randint(15, 120),
                price=0 if is_free else random.choice([49, 99, 149, 199, 249]),
                is_free=is_free,
                is_featured=random.random() > 0.75,
                is_trending=random.random() > 0.7,
                is_published=True,
                seo_keywords=f"{cat.name.lower()} interview questions, {tech.name.lower()} interview pdf",
                display_order=InterviewPDF.objects.filter(category=cat).count() + 1,
            )
            pdf.thumbnail.save(f"thumb-{i}.jpg", make_placeholder_image(cat.name), save=False)
            pdf.original_pdf.save(f"pdf-{i}.pdf", make_placeholder_pdf(title), save=False)
            pdf.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(categories)} categories, {len(technologies)} technologies, "
            f"{len(companies)} companies and {created} interview PDFs."
        ))
