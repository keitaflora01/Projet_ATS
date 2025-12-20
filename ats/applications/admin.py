from django.contrib import admin
from django.utils.html import format_html
from ats.applications.models.applications_model import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "submission_display",
        "cv_link",
        "portfolio_link",
        "other_documents_info",
    )
    search_fields = (
        "submission__candidate__user__email",
        "submission__candidate__user__full_name",
        "submission__job_offer__title",
    )
    readonly_fields = ("submission", "cv_preview", "portfolio_preview")
    autocomplete_fields = ("submission",)

    fieldsets = (
        ("Candidature liée", {"fields": ("submission",)}),
        ("Documents principaux", {
            "fields": (
                "cv_url",
                "cv_preview",
                "portfolio_url",
                "portfolio_preview",
            )
        }),
        ("Autres documents", {"fields": ("other_documents",)}),
    )

    def submission_display(self, obj):
        if obj.submission:
            candidate = obj.submission.candidate.user
            name = candidate.full_name or candidate.email
            job = obj.submission.job_offer.title
            return f"{name} → {job}"
        return "-"
    submission_display.short_description = "Candidature"

    def cv_link(self, obj):
        if obj.cv_url:
            return format_html('<a href="{}" target="_blank">📄 CV</a>', obj.cv_url)
        return "(Aucun)"
    cv_link.short_description = "CV"

    def cv_preview(self, obj):
        if obj.cv_url:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir le CV</a>', obj.cv_url)
        return "(Aucun CV)"
    cv_preview.short_description = "CV"

    def portfolio_link(self, obj):
        if obj.portfolio_url:
            return format_html('<a href="{}" target="_blank">🌐 Portfolio</a>', obj.portfolio_url)
        return "(Aucun)"
    portfolio_link.short_description = "Portfolio"

    def portfolio_preview(self, obj):
        if obj.portfolio_url:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir le Portfolio</a>', obj.portfolio_url)
        return "(Aucun portfolio)"
    portfolio_preview.short_description = "Portfolio"

    def other_documents_info(self, obj):
        if obj.other_documents:
            return "📎 Oui"
        return "(Aucun)"
    other_documents_info.short_description = "Autres docs"