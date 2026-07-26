from django.conf import settings
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    pdf = models.ForeignKey("pdfs.InterviewPDF", on_delete=models.CASCADE, related_name="orders")

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")

    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)

    invoice_number = models.CharField(max_length=30, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user} - {self.pdf} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils.crypto import get_random_string
            self.invoice_number = f"CIQ-{get_random_string(8).upper()}"
        super().save(*args, **kwargs)
