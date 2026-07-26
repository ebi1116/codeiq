import hmac
import hashlib
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.pdfs.models import InterviewPDF
from .models import Order

try:
    import razorpay
except ImportError:  # pragma: no cover
    razorpay = None


def _get_client():
    if not razorpay or not settings.RAZORPAY_KEY_ID:
        return None
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def create_order(request, slug):
    pdf = get_object_or_404(InterviewPDF, slug=slug, is_published=True)

    if pdf.is_free:
        messages.info(request, "This PDF is free — no purchase required.")
        return redirect(pdf.get_absolute_url())

    if pdf.user_has_access(request.user):
        messages.info(request, "You already own this PDF.")
        return redirect(pdf.get_absolute_url())

    client = _get_client()
    amount_paise = int(pdf.price * 100)

    if client is None:
        # Razorpay keys not configured yet (e.g. local dev) — explain instead of crashing.
        messages.warning(
            request,
            "Payments aren't configured yet. Add RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET "
            "to your .env to enable premium purchases.",
        )
        return redirect(pdf.get_absolute_url())

    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {"pdf_slug": pdf.slug, "user_id": request.user.id},
    })

    order = Order.objects.create(
        user=request.user,
        pdf=pdf,
        amount=pdf.price,
        currency="INR",
        status="created",
        razorpay_order_id=razorpay_order["id"],
    )

    context = {
        "pdf": pdf,
        "order": order,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_paise": amount_paise,
        "callback_url": request.build_absolute_uri(reverse("orders:verify_payment")),
    }
    return render(request, "orders/checkout.html", context)


@login_required
@require_POST
def verify_payment(request):
    data = request.POST or json.loads(request.body or "{}")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id, user=request.user)

    client = _get_client()
    verified = False
    if client is not None:
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            })
            verified = True
        except razorpay.errors.SignatureVerificationError:
            verified = False
    else:
        # Fallback manual HMAC check if the SDK isn't available.
        generated_signature = hmac.new(
            key=settings.RAZORPAY_KEY_SECRET.encode(),
            msg=f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()
        verified = hmac.compare_digest(generated_signature, razorpay_signature or "")

    if verified:
        order.status = "paid"
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.paid_at = timezone.now()
        order.save()
        return JsonResponse({"status": "success", "redirect_url": order.pdf.get_absolute_url()})

    order.status = "failed"
    order.save()
    return JsonResponse({"status": "failure"}, status=400)


@login_required
def invoice_detail(request, invoice_number):
    order = get_object_or_404(Order, invoice_number=invoice_number, user=request.user, status="paid")
    return render(request, "orders/invoice.html", {"order": order})
