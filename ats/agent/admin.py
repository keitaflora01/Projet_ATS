from django.contrib import admin
from django.utils.html import format_html

from ats.agent.models.analysis_result import AIAnalysisResult


class AIAnalysisResultInline(admin.TabularInline):
    model = AIAnalysisResult
    extra = 0
    can_delete = False
    readonly_fields = (
        "matching_score",
        "recommendation",
        "confidence",
        "processed_at",
        "raw_preview",
    )
    fields = (
        "matching_score",
        "recommendation",
        "confidence",
        "processed_at",
        "raw_preview",
    )
    show_change_link = True

    def raw_preview(self, obj):
        if obj.raw_ai_response:
            return str(obj.raw_ai_response)[:150] + "..." if len(str(obj.raw_ai_response)) > 150 else str(obj.raw_ai_response)
        return "-"
    raw_preview.short_description = "Réponse IA brute (aperçu)"


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = (
        "submission_display",
        "score_colored",
        "recommendation_badge",
        "confidence_display",
        "processed_at",
        "raw_preview",
    )
    list_filter = ("recommendation", "processed_at")
    search_fields = (
        "submission__candidate__email",
        "submission__job_offer__title",
        "recommendation_reason",
        "raw_text_response",
    )
    readonly_fields = (
        "submission",
        "matching_score",
        "matching_details",
        "extracted_profile",
        "recommendation",
        "recommendation_reason",
        "confidence",
        "ai_model_version",
        "processed_at",
        "processing_duration",
        "raw_ai_response",
        "raw_text_response",
    )
    date_hierarchy = "processed_at"
    ordering = ("-processed_at",)

    fieldsets = (
        ("Candidature", {"fields": ("submission",)}),
        ("Résultat principal", {
            "fields": ("matching_score", "confidence", "recommendation", "recommendation_reason"),
        }),
        ("Détails IA", {
            "fields": ("extracted_profile", "matching_details"),
            "classes": ("collapse",),
        }),
        ("Réponse brute (stockage complet)", {
            "fields": ("raw_ai_response", "raw_text_response"),
            "classes": ("collapse",),
        }),
        ("Métadonnées", {
            "fields": ("processed_at", "processing_duration", "ai_model_version"),
            "classes": ("collapse",),
        }),
    )

    # AFFICHAGE SCORE COLORÉ (ici, pas dans le modèle)
    def score_colored(self, obj):
        score = obj.matching_score
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        return format_html('<strong style="color:{};">{} / 100</strong>', color, score)
    score_colored.short_description = "Score"  # ← Maintenant ça marche !

    def submission_display(self, obj):
        if obj.submission:
            candidate = obj.submission.candidate.get_full_name() or obj.submission.candidate.email
            job = obj.submission.job_offer.title
            return f"{candidate} → {job}"
        return "-"
    submission_display.short_description = "Candidature"

    def recommendation_badge(self, obj):
        colors = {
            "interview_high": "green",
            "interview_medium": "#4CAF50",
            "interview_low": "orange",
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

    def confidence_display(self, obj):
        conf = obj.confidence * 100
        color = "green" if conf >= 80 else "orange" if conf >= 60 else "red"
        return format_html('<strong style="color:{};">{:.0f}%</strong>', color, conf)
    confidence_display.short_description = "Confiance"

    def raw_preview(self, obj):
        if obj.raw_ai_response:
            return str(obj.raw_ai_response)[:150] + "..." if len(str(obj.raw_ai_response)) > 150 else str(obj.raw_ai_response)
        return "-"
    raw_preview.short_description = "Réponse IA brute (aperçu)"