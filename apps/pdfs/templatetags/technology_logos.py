"""Local, brand-logo lookup used anywhere a technology card is rendered."""

from django import template
from django.templatetags.static import static


register = template.Library()

# Filenames are Simple Icons slugs unless an alias is necessary.  Files are
# downloaded to static/images/technology-logos by download_technology_logos.
LOGO_FILENAMES = {
    "android": "android", "angular": "angular", "ansible": "ansible",
    "apache": "apache", "argocd": "argo", "asp.net core": "dotnet",
    "aws": "amazonaws", "azure": "microsoftazure", "microsoft azure": "microsoftazure",
    "bash": "gnubash", "bitbucket": "bitbucket", "bootstrap": "bootstrap",
    "burp suite": "portswigger", "c": "c", "c#": "csharp", "c++": "cplusplus",
    "cassandra": "apachecassandra", "chef": "chef", "cloudflare": "cloudflare", "css": "css3",
    "cypress": "cypress", "dart": "dart", "digitalocean": "digitalocean",
    "django": "django", "docker": "docker", "dynamodb": "amazondynamodb",
    "elasticsearch": "elasticsearch", "express.js": "express", "fastapi": "fastapi",
    "firebase": "firebase", "firebase firestore": "firebase", "flask": "flask",
    "flutter": "flutter", "git": "git", "github": "github", "github actions": "githubactions",
    "gitlab": "gitlab", "go": "go", "google cloud": "googlecloud",
    "google cloud platform (gcp)": "googlecloud", "grafana": "grafana", "graphql": "graphql",
    "helm": "helm", "heroku": "heroku", "html": "html5", "hugging face": "huggingface",
    "ibm cloud": "ibm", "ionic": "ionic", "java": "openjdk", "javascript": "javascript",
    "jenkins": "jenkins", "jmeter": "apachejmeter", "julia": "julia", "kali linux": "kalilinux",
    "keras": "keras", "kotlin": "kotlin", "kubernetes": "kubernetes", "langchain": "langchain",
    "laravel": "laravel", "linux": "linux", "lua": "lua", "matlab": "mathworks",
    "maven": "apachemaven", "metasploit": "metasploit", "mongodb": "mongodb", "mysql": "mysql",
    # Nmap has no Simple Icons mark; Kali Linux is the closest security-tool
    # mark in the local catalogue.
    "netlify": "netlify", "next.js": "nextdotjs", "nginx": "nginx", "nmap": "kalilinux",
    "node.js": "nodedotjs", "numpy": "numpy", "nuxt.js": "nuxtdotjs", "objective-c": "apple",
    "openai": "openai", "opencv": "opencv", "oracle": "oracle", "oracle cloud": "oracle", "owasp": "owasp",
    "pandas": "pandas", "perl": "perl", "php": "php", "playwright": "playwright", "power bi": "powerbi",
    "postgresql": "postgresql", "postman": "postman", "powershell": "powershell",
    "prometheus": "prometheus", "puppet": "puppet", "python": "python", "pytorch": "pytorch",
    "r": "r", "react": "react", "react native": "react", "redis": "redis", "ruby": "ruby", "scala": "scala",
    "ruby on rails": "rubyonrails", "rust": "rust", "scikit-learn": "scikitlearn",
    "selenium": "selenium", "sentry": "sentry", "svelte": "svelte", "swift": "swift", "sqlite": "sqlite",
    # These products do not publish a Simple Icons asset. Use the closest
    # maintained product/ecosystem mark rather than a generic code glyph.
    "sql server": "microsoftazure", "sonarqube": "jenkins", "spring boot": "openjdk",
    "tailwind css": "tailwindcss", "tensorflow": "tensorflow", "terraform": "terraform",
    "tableau": "microsoftazure", "typescript": "typescript", "ubuntu": "ubuntu", "vercel": "vercel", "visual basic": "dotnet",
    "vue.js": "vuedotjs", "wireshark": "wireshark", "windows": "windows", "xamarin": "dotnet", "excel": "microsoftazure",
    "macos": "apple", "matplotlib": "python", "owasp": "kalilinux", "power bi": "microsoftazure", "scala": "openjdk", "sqlite": "postgresql",
}


@register.simple_tag
def technology_logo(name):
    """Return a local official/recognizable SVG path for every technology."""
    filename = LOGO_FILENAMES.get(str(name).strip().casefold(), "topic")
    return static(f"images/technology-logos/{filename}.svg")
