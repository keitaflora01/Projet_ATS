# ats/submissions/admin.py
from django.contrib import admin
from django.utils.html import format_html

from ats.submissions.models.submissions_models import Submission, SubmissionStatus


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "candidate_display",
        "job_offer_title",
        "status_badge",
        "submitted_at",
    )
    list_filter = ("status", "submitted_at", "job_offer__recruiter__company_name")
    search_fields = (
        "candidate__user__email",
        "candidate__user__full_name",
        "job_offer__title",
        "job_offer__recruiter__company_name",
    )
    readonly_fields = ("submitted_at", "updated_at")
    autocomplete_fields = ("candidate", "job_offer")
    date_hierarchy = "submitted_at"
    ordering = ("-submitted_at",)

    fieldsets = (
        ("Candidature", {
            "fields": (
                "candidate",
                "job_offer",
                "status",
            )
        }),
        ("Lettre de motivation", {
            "fields": ("cover_letter",),
            "classes": ("collapse",),
        }),
        ("Dates", {
            "fields": ("submitted_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def candidate_display(self, obj):
        user = obj.candidate.user
        name = user.full_name or user.email
        return f"{name} ({user.email})"
    candidate_display.short_description = "Candidat"
    candidate_display.admin_order_field = "candidate__user__email"

    def job_offer_title(self, obj):
        return obj.job_offer.title
    job_offer_title.short_description = "Offre"
    job_offer_title.admin_order_field = "job_offer__title"

    def status_badge(self, obj):
        colors = {
            SubmissionStatus.SUBMITTED: "gray",
            SubmissionStatus.UNDER_REVIEW: "blue",
            SubmissionStatus.INTERVIEW_SCHEDULED: "purple",
            SubmissionStatus.ACCEPTED: "green",
            SubmissionStatus.REJECTED: "red",
        }
        color = colors.get(obj.status, "gray")
        text = obj.get_status_display()
        return format_html(
            '<span style="background:{}; color:white; padding:4px 10px; border-radius:4px; font-size:0.9em;">{}</span>',
            color, text
        )
    status_badge.short_description = "Statut"