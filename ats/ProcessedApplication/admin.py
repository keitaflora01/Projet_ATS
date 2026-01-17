# ats/applications/admin.py (ajoute ou remplace la partie ProcessedApplication)

from django.contrib import admin
from django.utils.html import format_html

# Import the ProcessedApplication model class (was incorrectly importing the package)
from ats.ProcessedApplication.models.processed_application import ProcessedApplication
from ats.applications.models.applications_model import Application


class ProcessedApplicationInline(admin.TabularInline):
    model = ProcessedApplication
    extra = 0
    can_delete = False
    readonly_fields = (
        "matching_score_display",
        "recommendation_badge",
        "processed_at",
        "is_visible_display",
    )
    fields = (
        "matching_score_display",
        "recommendation_badge",
        "recommendation_reason",
        "processed_at",
        "is_visible_display",
    )

    def has_add_permission(self, request, obj=None):
        return False  # Créé automatiquement par l'IA

    def matching_score_display(self, obj):
        score = obj.matching_score or 0
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        return format_html('<strong style="color:{}; font-size:1.2em;">{}/100</strong>', color, score)
    matching_score_display.short_description = "Score IA"

    def recommendation_badge(self, obj):
        colors = {
            "interview": "green",
            "wait": "orange",
            "reject": "red",
        }
        color = colors.get(obj.recommendation, "gray")
        text = obj.get_recommendation_display()
        return format_html(
            '<span style="background:{}; color:white; padding:6px 12px; border-radius:6px; font-weight:bold;">{}</span>',
            color, text
        )
    recommendation_badge.short_description = "Recommandation"

    def is_visible_display(self, obj):
        if obj.is_visible_to_recruiter:
            return format_html('<span style="color:green; font-weight:bold;">✔ Visible</span>')
        return format_html('<span style="color:orange;">⌛ En attente</span>')
    is_visible_display.short_description = "Visibilité"


@admin.register(ProcessedApplication)
class ProcessedApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "application_display",
        "matching_score_display",
        "recommendation_badge",
        "processed_at",
        "is_visible_display",
    )
    list_filter = ("recommendation", "is_visible_to_recruiter", "processed_at")
    search_fields = (
        "application__submission__candidate__email",
        "application__submission__job_offer__title",
    )
    readonly_fields = (
        "application",
        "matching_score",
        "matching_details",
        "extracted_profile",
        "recommendation_reason",
        "processed_at",
        "is_visible_to_recruiter",
    )
    date_hierarchy = "processed_at"
    ordering = ("-processed_at",)

    fieldsets = (
        ("Candidature liée", {"fields": ("application",)}),
        ("Résultats Agent 1 - Extraction", {
            "fields": ("extracted_profile",),
            "classes": ("collapse",),
        }),
        ("Résultats Agent 2 - Matching", {
            "fields": ("matching_score", "matching_details"),
        }),
        ("Résultats Agent 3 - Recommandation", {
            "fields": ("recommendation", "recommendation_reason"),
        }),
        ("Métadonnées", {
            "fields": ("processed_at", "is_visible_to_recruiter"),
            "classes": ("collapse",),
        }),
    )

    def application_display(self, obj):
        if obj.application and obj.application.submission:
            candidate = obj.application.submission.candidate.get_full_name() or obj.application.submission.candidate.email
            job = obj.application.submission.job_offer.title
            return f"{candidate} → {job}"
        return "-"
    application_display.short_description = "Candidature"

    def matching_score_display(self, obj):
        score = obj.matching_score or 0
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        return format_html('<strong style="color:{};">{}/100</strong>', color, score)
    matching_score_display.short_description = "Score"

    def recommendation_badge(self, obj):
        colors = {
            "interview": "green",
            "wait": "orange",
            "reject": "red",
        }
        color = colors.get(obj.recommendation, "gray")
        text = obj.get_recommendation_display()
        return format_html(
            '<span style="background:{}; color:white; padding:6px 12px; border-radius:6px; font-weight:bold;">{}</span>',
            color, text
        )
    recommendation_badge.short_description = "Recommandation"

    def is_visible_display(self, obj):
        if obj.is_visible_to_recruiter:
            return format_html('<span style="color:green; font-weight:bold;">✔ Visible</span>')
        return format_html('<span style="color:orange;">⌛ En attente</span>')
    is_visible_display.short_description = "Visibilité"