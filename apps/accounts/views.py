from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .models import Profile, Wishlist, Bookmark, RecentlyViewed, DownloadHistory
from apps.orders.models import Order


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
    login_url = "/accounts/google/login/"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["purchased_count"] = Order.objects.filter(user=user, status="paid").count()
        ctx["free_downloads_count"] = DownloadHistory.objects.filter(
            user=user, pdf__is_free=True
        ).values("pdf").distinct().count()
        ctx["wishlist_count"] = Wishlist.objects.filter(user=user).count()
        ctx["bookmarks_count"] = Bookmark.objects.filter(user=user).count()
        ctx["recent_orders"] = Order.objects.filter(user=user).order_by("-created_at")[:5]
        ctx["recently_viewed"] = RecentlyViewed.objects.filter(user=user)[:6]
        return ctx


class PurchasesView(LoginRequiredMixin, ListView):
    template_name = "accounts/purchases.html"
    context_object_name = "orders"
    login_url = "/accounts/google/login/"
    paginate_by = 12

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status="paid")


class FreeDownloadsView(LoginRequiredMixin, ListView):
    template_name = "accounts/free_downloads.html"
    context_object_name = "downloads"
    login_url = "/accounts/google/login/"
    paginate_by = 12

    def get_queryset(self):
        return DownloadHistory.objects.filter(user=self.request.user, pdf__is_free=True)


class RecentlyViewedView(LoginRequiredMixin, ListView):
    template_name = "accounts/recently_viewed.html"
    context_object_name = "views"
    login_url = "/accounts/google/login/"
    paginate_by = 12

    def get_queryset(self):
        return RecentlyViewed.objects.filter(user=self.request.user)


class WishlistView(LoginRequiredMixin, ListView):
    template_name = "accounts/wishlist.html"
    context_object_name = "items"
    login_url = "/accounts/google/login/"
    paginate_by = 12

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class BookmarksView(LoginRequiredMixin, ListView):
    template_name = "accounts/bookmarks.html"
    context_object_name = "items"
    login_url = "/accounts/google/login/"
    paginate_by = 12

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)


class InvoicesView(LoginRequiredMixin, ListView):
    template_name = "accounts/invoices.html"
    context_object_name = "orders"
    login_url = "/accounts/google/login/"
    paginate_by = 12

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status="paid")


class SettingsView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ["headline", "bio", "avatar_url"]
    template_name = "accounts/settings.html"
    success_url = reverse_lazy("accounts:settings")
    login_url = "/accounts/google/login/"

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["headline"].widget.attrs.update({"class": "ciq-input"})
        form.fields["avatar_url"].widget.attrs.update({"class": "ciq-input"})
        form.fields["bio"].widget.attrs.update({"class": "ciq-textarea", "rows": 4})
        return form

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated.")
        return super().form_valid(form)
