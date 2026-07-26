from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number", "user", "pdf", "amount", "currency",
        "status_badge", "razorpay_order_id", "created_at", "paid_at",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = ("invoice_number", "user__username", "user__email", "pdf__title", "razorpay_order_id")
    readonly_fields = ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature",
                        "invoice_number", "created_at", "paid_at")
    date_hierarchy = "created_at"

    def status_badge(self, obj):
        from django.utils.html import format_html
        colors = {"paid": "#059669", "created": "#D97706", "failed": "#DC2626"}
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            colors.get(obj.status, "#666"), obj.get_status_display()
        )
    status_badge.short_description = "Status"
