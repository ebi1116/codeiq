from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import InterviewPDF, Technology


class InterviewPDFAdminForm(forms.ModelForm):
    """Admin editor for all PDF content, including legacy file storage."""

    class Meta:
        model = InterviewPDF
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "original_pdf" in self.fields:
            self.fields["original_pdf"].required = False
        self.fields["technology"].required = True
        self.fields["pdf_file"].label = "PDF"
        category_id = self.data.get("category") or getattr(self.instance, "category_id", None)
        if category_id:
            self.fields["technology"].queryset = Technology.objects.filter(
                Q(categories=category_id) | Q(category_id=category_id)
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        legacy_pdf = getattr(self.instance, "original_pdf", None)
        if not legacy_pdf and not cleaned_data.get("pdf_file"):
            raise ValidationError("Upload a PDF.")
        if cleaned_data.get("is_premium") and not cleaned_data.get("price"):
            self.add_error("price", "Enter a price greater than zero for premium content.")
        cleaned_data["is_free"] = not cleaned_data.get("is_premium", False)
        return cleaned_data
