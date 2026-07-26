from django.core.management.base import BaseCommand

from apps.pdfs.models import Category, Technology


# Keys represent a category hierarchy. Technologies remain standalone records,
# so an administrator can later move them between categories without code changes.
CATALOG = [
    ("Programming Languages", None, "fa-code", [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "Kotlin", "Swift", "Dart", "PHP", "Ruby", "R", "Scala", "Perl", "Lua", "Julia", "MATLAB", "Objective-C", "Visual Basic", "Shell Scripting", "Bash", "PowerShell",
    ]),
    ("Web Development", None, "fa-globe", []),
    ("Frontend", "Web Development", "fa-display", [
        "HTML", "CSS", "JavaScript", "Bootstrap", "Tailwind CSS", "React", "Angular", "Vue.js", "Next.js", "Nuxt.js", "Svelte",
    ]),
    ("Backend", "Web Development", "fa-server", [
        "Django", "Flask", "FastAPI", "Node.js", "Express.js", "Spring Boot", "Laravel", "ASP.NET Core", "Ruby on Rails",
    ]),
    ("API", "Web Development", "fa-plug", ["REST API", "GraphQL", "WebSocket"]),
    ("Mobile Development", None, "fa-mobile-screen", [
        "Android", "Java Android", "Kotlin Android", "Flutter", "React Native", "Swift iOS", "Xamarin", "Ionic",
    ]),
    ("Database", None, "fa-database", [
        "SQL", "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Firebase Firestore",
    ]),
    ("Cloud Computing", None, "fa-cloud", [
        "AWS", "Microsoft Azure", "Google Cloud Platform (GCP)", "Oracle Cloud", "IBM Cloud", "DigitalOcean", "Linode", "Vultr", "Alibaba Cloud", "Cloudflare", "Heroku", "Render", "Railway", "Vercel", "Netlify",
    ]),
    ("AWS Services", "Cloud Computing", "fa-aws", [
        "EC2", "S3", "IAM", "RDS", "Lambda", "API Gateway", "Route53", "CloudFront", "ECS", "EKS", "Elastic Beanstalk", "CloudWatch", "SNS", "SQS", "SES", "DynamoDB", "VPC", "ELB", "Auto Scaling", "ECR", "Systems Manager", "Secrets Manager",
    ]),
    ("Azure Services", "Cloud Computing", "fa-cloud", [
        "Virtual Machines", "Blob Storage", "Azure SQL", "Functions", "App Services", "AKS", "DevOps", "Monitor",
    ]),
    ("GCP Services", "Cloud Computing", "fa-cloud", [
        "Compute Engine", "Cloud Storage", "Cloud Run", "BigQuery", "Cloud Functions", "Kubernetes Engine", "Firebase", "DevOps",
    ]),
    ("DevOps", None, "fa-gears", [
        "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", "Bitbucket", "CI/CD", "GitHub Actions", "Terraform", "Ansible", "Puppet", "Chef", "Helm", "ArgoCD", "Prometheus", "Grafana", "ELK Stack", "SonarQube", "Nexus", "Maven", "Gradle", "Linux", "Nginx", "Apache",
    ]),
    ("Artificial Intelligence", None, "fa-brain", [
        "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Generative AI", "LLM", "Prompt Engineering", "OpenAI", "LangChain", "RAG", "AI Agents", "TensorFlow", "PyTorch", "Keras", "Hugging Face", "Scikit-learn",
    ]),
    ("Data Science", None, "fa-chart-line", [
        "NumPy", "Pandas", "Matplotlib", "Seaborn", "Statistics", "Data Analysis", "Data Visualization", "Feature Engineering", "EDA", "Power BI", "Tableau", "Excel",
    ]),
    ("Cyber Security", None, "fa-shield-halved", [
        "Ethical Hacking", "Network Security", "Kali Linux", "OWASP", "Burp Suite", "Penetration Testing", "Cryptography", "SIEM", "SOC",
    ]),
    ("Software Testing", None, "fa-vial", [
        "Manual Testing", "Automation Testing", "Selenium", "Cypress", "Playwright", "Postman", "JMeter", "API Testing", "Unit Testing", "Integration Testing",
    ]),
    ("Operating Systems", None, "fa-desktop", ["Linux", "Ubuntu", "Windows", "macOS"]),
    ("Networking", None, "fa-network-wired", ["CCNA", "TCP/IP", "DNS", "HTTP", "HTTPS", "VPN", "Routing", "Switching"]),
    ("Aptitude", None, "fa-calculator", ["Quantitative Aptitude", "Logical Reasoning", "Verbal Ability", "Data Interpretation"]),
    ("Interview Preparation", None, "fa-comments", [
        "HR Interview Questions", "Technical Interview Questions", "System Design", "Coding Interview", "Resume Tips", "Group Discussion", "Behavioral Questions",
    ]),
    ("DSA", None, "fa-diagram-project", [
        "Arrays", "Strings", "Linked List", "Stack", "Queue", "Trees", "Graph", "Heap", "Hashing", "Dynamic Programming", "Greedy", "Backtracking", "Recursion", "Searching", "Sorting",
    ]),
]


class Command(BaseCommand):
    help = "Create the complete database-driven CodeIQ technology catalog. Safe to run repeatedly."

    def handle(self, *args, **options):
        categories = {}
        technologies_created = 0

        for order, (name, parent_name, icon, technologies) in enumerate(CATALOG):
            parent = categories.get(parent_name) if parent_name else None
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    "parent": parent,
                    "icon": icon,
                    "description": f"Curated {name} learning resources and interview preparation PDFs.",
                    "order": order,
                    "display_order": order + 1,
                },
            )
            categories[name] = category

            # Existing records are retained. Only fill missing organization and metadata.
            updates = []
            if category.parent_id != (parent.id if parent else None) and not category.pdfs.exists():
                category.parent = parent
                updates.append("parent")
            if not category.icon:
                category.icon = icon
                updates.append("icon")
            if not category.description:
                category.description = f"Curated {name} learning resources and interview preparation PDFs."
                updates.append("description")
            if updates:
                category.save(update_fields=updates + ["updated_at"])

            for technology_order, technology_name in enumerate(technologies):
                technology, was_created = Technology.objects.get_or_create(
                    name=technology_name,
                    defaults={
                        "category": category,
                        "icon": icon,
                        "description": f"Explore {technology_name} interview questions, learning resources, and preparation PDFs.",
                        "seo_title": f"{technology_name} Interview Questions and PDFs | CodeIQ",
                        "seo_description": f"Prepare for {technology_name} interviews with curated PDFs, topics, and practical questions.",
                        "seo_keywords": f"{technology_name}, {technology_name} interview questions, {technology_name} PDF, programming learning",
                        "order": technology_order,
                    },
                )
                technologies_created += int(was_created)
                updates = []
                if technology.category_id is None:
                    technology.category = category
                    updates.append("category")
                if not technology.icon:
                    technology.icon = icon
                    updates.append("icon")
                if not technology.description:
                    technology.description = f"Explore {technology_name} interview questions, learning resources, and preparation PDFs."
                    updates.append("description")
                if not technology.seo_title:
                    technology.seo_title = f"{technology_name} Interview Questions and PDFs | CodeIQ"
                    updates.append("seo_title")
                if not technology.seo_description:
                    technology.seo_description = f"Prepare for {technology_name} interviews with curated PDFs, topics, and practical questions."
                    updates.append("seo_description")
                if not technology.seo_keywords:
                    technology.seo_keywords = f"{technology_name}, {technology_name} interview questions, {technology_name} PDF, programming learning"
                    updates.append("seo_keywords")
                if updates:
                    technology.save(update_fields=updates + ["updated_at"])
                technology.categories.add(category)

        self.stdout.write(self.style.SUCCESS(
            f"Catalog ready: {len(categories)} categories and {technologies_created} new technologies created."
        ))
