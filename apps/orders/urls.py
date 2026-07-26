from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/<slug:slug>/", views.create_order, name="create_order"),
    path("verify/", views.verify_payment, name="verify_payment"),
    path("invoice/<str:invoice_number>/", views.invoice_detail, name="invoice_detail"),
]
