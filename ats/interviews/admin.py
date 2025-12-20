# ats/interviews/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from ats.interviews.models.interviews_model import Interview, InterviewStatus


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        "submission_display",
        "interview_type",
        "scheduled_at_formatted",
        "status_badge",
        "location_or_link_preview",
    )
    list_filter = (
        "status",
        "interview_type",
        "scheduled_at",
    )
    search_fields = (
        "submission__candidate__user__email",
        "submission__candidate__user__full_name",
        "submission__job_offer__title",
        "location_or_link",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("submission",)
    date_hierarchy = "scheduled_at"
    ordering = ("-scheduled_at",)

    fieldsets = (
        ("Entretien", {
            "fields": (
                "submission",
                "interview_type",
                "scheduled_at",
                "status",
            )
        }),
        ("Lieu / Lien", {"fields": ("location_or_link",)}),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def submission_display(self, obj):
        if obj.submission:
            candidate_name = obj.submission.candidate.user.full_name or obj.submission.candidate.user.email
            job_title = obj.submission.job_offer.title
            return f"{candidate_name} → {job_title}"
        return "-"
    submission_display.short_description = "Candidature"

    def scheduled_at_formatted(self, obj):
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
            InterviewStatus.NO_SHOW: "orange",
        }
        color = colors.get(obj.status, "gray")
        text = obj.get_status_display()
        return format_html(
            '<span style="background:{}; color:white; padding:4px 10px; border-radius:4px;">{}</span>',
            color, text
        )
    status_badge.short_description = "Statut"

    def location_or_link_preview(self, obj):
        if not obj.location_or_link:
            return "-"
        value = obj.location_or_link.strip()
        if value.startswith(("http://", "https://")):
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir le lien</a>', value)
        return value
    location_or_link_preview.short_description = "Lieu / Lien"