from django import template
from django.templatetags.static import static


register = template.Library()


LANGUAGE_LOGOS = {
    "python": "python.svg", "java": "java.svg", "c": "c.svg",
    "c++": "cplusplus.svg", "c#": "csharp.svg",
    "javascript": "javascript.svg", "typescript": "typescript.svg",
    "go": "go.svg", "rust": "rust.svg", "kotlin": "kotlin.svg",
    "swift": "swift.svg", "dart": "dart.svg", "php": "php.svg",
    "ruby": "ruby.svg", "r": "r.svg", "scala": "scala.svg",
    "perl": "perl.svg", "lua": "lua.svg", "julia": "julia.svg",
    "matlab": "matlab.svg", "objective-c": "objective-c.svg",
    "visual basic": "visualbasic.svg", "shell scripting": "bash.svg",
    "bash": "bash.svg", "powershell": "powershell.svg",
}


@register.simple_tag
def language_logo(name):
    """Return a local SVG for known programming-language technology records."""
    filename = LANGUAGE_LOGOS.get(str(name).casefold())
    return static(f"images/language-logos/{filename}") if filename else ""
