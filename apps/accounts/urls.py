from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="dashboard"),
    path("purchases/", views.PurchasesView.as_view(), name="purchases"),
    path("free-downloads/", views.FreeDownloadsView.as_view(), name="free_downloads"),
    path("recently-viewed/", views.RecentlyViewedView.as_view(), name="recently_viewed"),
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
    path("bookmarks/", views.BookmarksView.as_view(), name="bookmarks"),
    path("invoices/", views.InvoicesView.as_view(), name="invoices"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
]
