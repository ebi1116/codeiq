from django.contrib import admin
from .models import Profile, Wishlist, Bookmark, RecentlyViewed, DownloadHistory


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "created_at")
    search_fields = ("user__username", "user__email", "headline")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "pdf", "added_at")
    search_fields = ("user__username", "pdf__title")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "pdf", "added_at")
    search_fields = ("user__username", "pdf__title")


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ("user", "pdf", "viewed_at")
    search_fields = ("user__username", "pdf__title")


@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "pdf", "downloaded_at")
    search_fields = ("user__username", "pdf__title")
