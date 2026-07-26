from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    avatar_url = models.URLField(blank=True)
    headline = models.CharField(max_length=150, blank=True, help_text="e.g. Aspiring Django Developer")
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.get_username()}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    pdf = models.ForeignKey("pdfs.InterviewPDF", on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "pdf")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} \u2665 {self.pdf}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    pdf = models.ForeignKey("pdfs.InterviewPDF", on_delete=models.CASCADE, related_name="bookmarked_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "pdf")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} bookmarked {self.pdf}"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recently_viewed")
    pdf = models.ForeignKey("pdfs.InterviewPDF", on_delete=models.CASCADE, related_name="viewed_by")
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "pdf")
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.user} viewed {self.pdf}"


class DownloadHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="download_history")
    pdf = models.ForeignKey("pdfs.InterviewPDF", on_delete=models.CASCADE, related_name="download_logs")
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-downloaded_at"]

    def __str__(self):
        return f"{self.user} downloaded {self.pdf}"
