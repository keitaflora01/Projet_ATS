from django.utils.html import format_html
from ats.agent.models.analysis_result import AIAnalysisResult
from django.contrib import admin

class AIAnalysisResultInline(admin.TabularInline):
    """Inline to show the AIAnalysisResult on the Submission admin page."""
    model = AIAnalysisResult
    extra = 0
    can_delete = False
    readonly_fields = (
        "matching_score",
        "recommendation",
        "processed_at",
        "confidence",
    )
    fields = (
        "matching_score",
        "recommendation",
        "recommendation_reason",
        "processed_at",
        "confidence",
    )
    show_change_link = True


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = (
        "submission_display",
        "matching_score_display",
        "recommendation_badge",
        "confidence_display",
        "processed_at",
    )
    list_filter = ("recommendation", "processed_at")
    search_fields = (
        "submission__candidate__email",
        "submission__job_offer__title",
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
    )
    date_hierarchy = "processed_at"
    ordering = ("-processed_at",)

    fieldsets = (
        ("Candidature liée", {"fields": ("submission",)}),
        ("Résultat global", {
            "fields": ("matching_score", "confidence", "recommendation", "recommendation_reason"),
        }),
        ("Détails techniques", {
            "fields": ("extracted_profile", "matching_details"),
            "classes": ("collapse",),
        }),
        ("Métadonnées", {
            "fields": ("processed_at", "processing_duration", "ai_model_version"),
            "classes": ("collapse",),
        }),
    )

    def submission_display(self, obj):
        if obj.submission:
            candidate = obj.submission.candidate.get_full_name() or obj.submission.candidate.email
            job = obj.submission.job_offer.title
            return f"{candidate} → {job}"
        return "-"
    submission_display.short_description = "Candidature"

    def matching_score_display(self, obj):
        score = obj.matching_score
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        return format_html('<strong style="color:{};">{} / 100</strong>', color, score)
    matching_score_display.short_description = "Score"

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
    