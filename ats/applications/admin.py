# ats/applications/admin.py
from django.contrib import admin
from django.utils.html import format_html
from ats.applications.models.applications_model import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "submission_display",
        "candidate_name",
        "job_title",
        "ia_score_display",
        "cv_link",
        "cover_letter_link",
        "portfolio_link",
    )
    list_filter = ("submission__created", "ia_score")
    search_fields = (
        "submission__candidate__email",
        "submission__candidate__full_name",
        "submission__job_offer__title",
    )
    readonly_fields = (
        "submission",
        "ia_score",
        "cv_preview",
        "cover_letter_preview",
        "portfolio_preview",
    )
    autocomplete_fields = ("submission",)

    fieldsets = (
        ("Candidature liée", {
            "fields": ("submission",)
        }),
        ("Informations professionnelles", {
            "fields": (
                "years_experience",
                "availability_date",
                "desired_salary",
            )
        }),
        ("Documents", {
            "fields": (
                "cv_preview",
                "cover_letter_preview",
                "portfolio_url",
                "portfolio_preview",
            )
        }),
        ("Analyse IA", {
            "fields": ("ia_score",),
            "classes": ("collapse",),
        }),
        ("Autres", {
            "fields": ("other_documents",),
            "classes": ("collapse",),
        }),
    )

    def candidate_name(self, obj):
        user = obj.submission.candidate  # ← Correction ici : c'est déjà un User
        return user.get_full_name() or user.email
    candidate_name.short_description = "Candidat"

    def job_title(self, obj):
        return obj.submission.job_offer.title
    job_title.short_description = "Offre"

    def submission_display(self, obj):
        if obj.submission:
            user = obj.submission.candidate  # ← Correction ici
            candidate = user.get_full_name() or user.email
            job = obj.submission.job_offer.title
            return f"{candidate} → {job}"
        return "-"
    submission_display.short_description = "Candidature"

    def ia_score_display(self, obj):
        score = obj.ia_score or 0
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        return format_html('<strong style="color:{};">{}/100</strong>', color, score)
    ia_score_display.short_description = "Score IA"

    def cv_link(self, obj):
        if obj.cv_file:
            return format_html('<a href="{}" target="_blank">📄 CV</a>', obj.cv_file.url)
        return "(Aucun)"
    cv_link.short_description = "CV"

    def cv_preview(self, obj):
        if obj.cv_file:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir CV</a>', obj.cv_file.url)
        return "(Aucun CV)"
    cv_preview.short_description = "CV"

    def cover_letter_link(self, obj):
        if obj.cover_letter_file:
            return format_html('<a href="{}" target="_blank">✉️ Lettre</a>', obj.cover_letter_file.url)
        return "(Aucune)"
    cover_letter_link.short_description = "Lettre"

    def cover_letter_preview(self, obj):
        if obj.cover_letter_file:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir lettre</a>', obj.cover_letter_file.url)
        return "(Aucune lettre)"
    cover_letter_preview.short_description = "Lettre de motivation"

    def portfolio_link(self, obj):
        if obj.portfolio_url:
            return format_html('<a href="{}" target="_blank">🌐 Portfolio</a>', obj.portfolio_url)
        return "(Aucun)"
    portfolio_link.short_description = "Portfolio"

    def portfolio_preview(self, obj):
        if obj.portfolio_url:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir portfolio</a>', obj.portfolio_url)
        return "(Aucun)"
    portfolio_preview.short_description = "Portfolio"