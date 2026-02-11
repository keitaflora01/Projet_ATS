# ats/interviews/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from ats.interviews.models.interview_model import Interview, InterviewStatus


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        "submission_display",
        "scheduled_at_formatted",
        "completed_at",
        "is_completed",
        "status_badge",
    )
    list_filter = (
        "status",
        "scheduled_at",
        "completed_at",
    )
    search_fields = (
        "application__submission__candidate__custom_user__email",
        "application__submission__candidate__custom_user__first_name",
        "job_offer__title",
    )
    readonly_fields = ("created", "modified", "questions_preview", "is_completed")
    autocomplete_fields = ("application", "job_offer")
    date_hierarchy = "scheduled_at"
    ordering = ("-scheduled_at",)

    fieldsets = (
        ("Entretien", {
            "fields": (
                "application",
                "job_offer",
                "scheduled_at",
                "status",
            )
        }),
        ("Questions & Notes", {"fields": ("questions_preview", "questions")}),
        ("Dates", {"fields": ("created", "modified", "completed_at"), "classes": ("collapse",)}),
    )

    def submission_display(self, obj):
        if obj.application and obj.application.submission:
            candidate_name = obj.application.submission.candidate.get_full_name() or obj.application.submission.candidate.email
            job_title = obj.job_offer.title
            return f"{candidate_name} → {job_title}"
        return "-"
    submission_display.short_description = "Candidature"

    def scheduled_at_formatted(self, obj):
        if not obj.scheduled_at:
            return "-"
        local_time = timezone.localtime(obj.scheduled_at)
        date_str = local_time.strftime("%d/%m/%Y %H:%M")
        if obj.scheduled_at < timezone.now():
            return format_html('<span style="color: gray;">{} (passé)</span>', date_str)
        return format_html('<span style="color: green; font-weight: bold;">{}</span>', date_str)
    scheduled_at_formatted.short_description = "Planifié le"

    def status_badge(self, obj):
        colors = {
            InterviewStatus.SCHEDULED: "blue",
            InterviewStatus.COMPLETED: "green",
            InterviewStatus.CANCELLED: "red",
            InterviewStatus.PENDING_FEEDBACK: "orange",
        }
        color = colors.get(obj.status, "gray")
        text = obj.get_status_display()
        return format_html(
            '<span style="background:{}; color:white; padding:4px 10px; border-radius:4px;">{}</span>',
            color, text
        )
    status_badge.short_description = "Statut"

    def questions_preview(self, obj):
        if obj.questions:
            return format_html("<pre>{}</pre>", str(obj.questions))
        return "-"
    questions_preview.short_description = "Questions (Aperçu)"

    def is_completed(self, obj):
        """Computed boolean shown in admin: True if completed_at set or status is COMPLETED."""
        if obj is None:
            return False
        return bool(obj.completed_at) or (getattr(obj, 'status', None) == InterviewStatus.COMPLETED)
    is_completed.short_description = "Complété"
    is_completed.boolean = True
    