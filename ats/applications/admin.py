from django.contrib import admin
from django.utils.html import format_html
from ats.applications.models.applications_model import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "submission_display",
        "cv_link",
        "cover_letter_link",
        "portfolio_link",
        "other_documents_info",
    )

    search_fields = (
        "submission__candidate__user__email",
        "submission__candidate__user__full_name",
        "submission__job_offer__title",
    )

    readonly_fields = (
        "submission",
        "cv_preview",
        "cover_letter_preview",
        "portfolio_preview",
    )

    autocomplete_fields = ("submission",)

    fieldsets = (
        ("Candidature liée", {"fields": ("submission",)}),
        ("Documents principaux", {
            "fields": (
                "cv_preview",
                "cover_letter_preview",
                "portfolio_url",
                "portfolio_preview",
            )
        }),
        ("Autres documents", {"fields": ("other_documents",)}),
    )

    def submission_display(self, obj):
        if obj.submission:
            user = obj.submission.candidate.user
            name = user.full_name or user.email
            job = obj.submission.job_offer.title
            return f"{name} → {job}"
        return "-"
    submission_display.short_description = "Candidature"

    def cv_link(self, obj):
        if obj.cv_file:
            return format_html('<a href="{}" target="_blank">📄 CV</a>', obj.cv_file.url)
        return "(Aucun)"
    cv_link.short_description = "CV"

    def cv_preview(self, obj):
        if obj.cv_file:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir le CV</a>', obj.cv_file.url)
        return "(Aucun CV)"
    cv_preview.short_description = "CV"

    def cover_letter_link(self, obj):
        if obj.cover_letter_file:
            return format_html('<a href="{}" target="_blank">📝 Lettre</a>', obj.cover_letter_file.url)
        return "(Aucune)"
    cover_letter_link.short_description = "Lettre"

    def cover_letter_preview(self, obj):
        if obj.cover_letter_file:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir la lettre</a>', obj.cover_letter_file.url)
        return "(Aucune lettre)"
    cover_letter_preview.short_description = "Lettre de motivation"

    def portfolio_link(self, obj):
        if obj.portfolio_url:
            return format_html('<a href="{}" target="_blank">🌐 Portfolio</a>', obj.portfolio_url)
        return "(Aucun)"
    portfolio_link.short_description = "Portfolio"

    def portfolio_preview(self, obj):
        if obj.portfolio_url:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir le portfolio</a>', obj.portfolio_url)
        return "(Aucun portfolio)"
    portfolio_preview.short_description = "Portfolio"

    def other_documents_info(self, obj):
        return "📎 Oui" if obj.other_documents else "(Aucun)"
    other_documents_info.short_description = "Autres docs"
