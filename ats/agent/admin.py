from django.contrib import admin
from django.utils.html import format_html

from ats.agent.models.analysis_result import AIAnalysisResult


class AIAnalysisResultInline(admin.TabularInline):
    model = AIAnalysisResult
    extra = 0  
    can_delete = False
    readonly_fields = (
        "score_display",
        "extracted_skills_preview",
        "matching_skills_preview",
        "missing_skills_preview",
        "summary_preview",
        "processed_at",
    )

    def has_add_permission(self, request, obj=None):
        return False  

    # Affichage joli du score avec couleur
    def score_display(self, obj):
        if obj.score >= 80:
            color = "green"
        elif obj.score >= 60:
            color = "orange"
        else:
            color = "red"
        return format_html(
            '<strong style="font-size:1.4em; color:{};">{} / 100</strong>',
            color, obj.score
        )
    score_display.short_description = "Score IA"

    # Aperçu des compétences (limité pour ne pas surcharger)
    def extracted_skills_preview(self, obj):
        skills = obj.extracted_skills or []
        preview = ", ".join(skills[:8])
        if len(skills) > 8:
            preview += f" ... (+{len(skills)-8})"
        return preview or "-"
    extracted_skills_preview.short_description = "Compétences extraites"

    def matching_skills_preview(self, obj):
        skills = obj.matching_skills or []
        return format_html(
            '<span style="color:green; font-weight:bold;">{}</span>',
            ", ".join(skills) or "-"
        )
    matching_skills_preview.short_description = "Correspondances ✓"

    def missing_skills_preview(self, obj):
        skills = obj.missing_skills or []
        return format_html(
            '<span style="color:red;">{}</span>',
            ", ".join(skills) or "-"
        )
    missing_skills_preview.short_description = "Manquantes ✗"

    def summary_preview(self, obj):
        summary = obj.summary or "Aucun résumé généré."
        if len(summary) > 300:
            summary = summary[:300] + " ..."
        return format_html('<div style="max-width:600px;">{}</div>', summary)
    summary_preview.short_description = "Résumé IA"


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ("submission", "score_display", "processed_at")
    list_filter = ("processed_at", "score")
    search_fields = ("submission__candidate__user__email", "submission__job_offer__title")
    readonly_fields = ("submission", "score", "extracted_skills", "matching_skills", "missing_skills", "summary", "raw_response", "processed_at")

    def score_display(self, obj):
        if obj.score >= 80:
            color = "green"
        elif obj.score >= 60:
            color = "orange"
        else:
            color = "red"
        return format_html('<strong style="color:{};">{}/100</strong>', color, obj.score)
    score_display.short_description = "Score"

    def has_add_permission(self, request):
        return False  

    def has_delete_permission(self, request, obj=None):
        return False 