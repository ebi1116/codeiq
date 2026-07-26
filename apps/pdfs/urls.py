from django.urls import path
from . import views

app_name = "pdfs"

urlpatterns = [
    path("pdfs/", views.PDFListView.as_view(), name="pdf_list"),
    path("pdfs/<slug:slug>/", views.PDFDetailView.as_view(), name="pdf_detail"),
    path("pdfs/<slug:slug>/download/", views.download_pdf, name="pdf_download"),
    path("pdfs/<slug:slug>/preview/", views.preview_pdf, name="pdf_preview"),
    path("pdfs/<slug:slug>/wishlist/", views.toggle_wishlist, name="toggle_wishlist"),
    path("pdfs/<slug:slug>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("technology/<slug:slug>/", views.TechnologyDetailView.as_view(), name="technology_detail"),
    path("company/<slug:slug>/", views.CompanyDetailView.as_view(), name="company_detail"),
]
