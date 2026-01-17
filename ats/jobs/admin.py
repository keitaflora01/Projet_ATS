# ats/jobs/admin.py
from django.contrib import admin
from django.utils.html import format_html
from ats.jobs.models.jobs_model import JobOffer, JobType, ContractType


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recruiter_display",
        "job_type_badge",
        "contract_type_badge",
        "location",
        "remote_badge",
        "active_badge",
        "salary_range",
        "skills_preview",
        "published_at",
    )
    list_filter = (
        "job_type",
        "contract_type",
        "is_remote",
        "is_active",
        "location",
        "published_at",
    )
    search_fields = (
        "title",
        "location",
        "description",
        "required_skills",
        "requirements",
        "recruiter__company_name",
        "recruiter__user__email",
    )
    readonly_fields = ("published_at", "is_expired")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    autocomplete_fields = ("recruiter",)

    fieldsets = (
        ("Informations principales", {
            "fields": (
                "recruiter",
                "title",
                "description",
                ("job_type", "contract_type"),
                "location",
                ("is_remote", "is_active"),
            )
        }),
        ("Contenu détaillé", {
            "fields": (
                "required_skills",
                "requirements",
            ),
            "classes": ("collapse",),
        }),
        ("Salaire & Expiration", {
            "fields": (
                ("salary_min", "salary_max"),
                "expires_at",
                "is_expired",
            )
        }),
        ("Dates", {
            "fields": ("published_at",),
            "classes": ("collapse",),
        }),
    )

    # Affichage du recruteur
    def recruiter_display(self, obj):
        if obj.recruiter:
            return f"{obj.recruiter.company_name} ({obj.recruiter.user.email})"
        return "-"
    recruiter_display.short_description = "Recruteur"
    recruiter_display.admin_order_field = "recruiter__company_name"

    # Badge pour job_type
    def job_type_badge(self, obj):
        colors = {
            JobType.FULL_TIME: "green",
            JobType.PART_TIME: "orange",
            JobType.REMOTE: "purple",
            JobType.HYBRID: "teal",
        }
        color = colors.get(obj.job_type, "gray")
        text = obj.get_job_type_display()
        return format_html(
            '<span style="background:{}; color:white; padding:4px 8px; border-radius:4px; font-size:0.9em;">{}</span>',
            color, text
        )
    job_type_badge.short_description = "Type de poste"

    # Badge pour contract_type
    def contract_type_badge(self, obj):
        colors = {
            ContractType.CDI: "green",
            ContractType.CDD: "blue",
            ContractType.ALTERNANCE: "orange",
            ContractType.STAGE: "purple",
            ContractType.FREELANCE: "teal",
            ContractType.INTERIM: "gray",
        }
        color = colors.get(obj.contract_type, "gray")
        text = obj.get_contract_type_display()
        return format_html(
            '<span style="background:{}; color:white; padding:4px 8px; border-radius:4px; font-size:0.9em;">{}</span>',
            color, text
        )
    contract_type_badge.short_description = "Contrat"

    # Badge remote
    def remote_badge(self, obj):
        if obj.is_remote:
            return format_html('<span style="color: green; font-weight: bold;">✓ Remote</span>')
        return format_html('<span style="color: gray;">Office</span>')
    remote_badge.short_description = "Remote"

    # Badge actif/inactif
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: red;">● Inactive</span>')
    active_badge.short_description = "Active"

    # Fourchette salaire
    def salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_min} – {obj.salary_max} €"
        elif obj.salary_min:
            return f"À partir de {obj.salary_min} €"
        elif obj.salary_max:
            return f"Jusqu’à {obj.salary_max} €"
        return "Non communiqué"
    salary_range.short_description = "Salaire"

    # Aperçu des compétences requises (premiers 50 caractères)
    def skills_preview(self, obj):
        if obj.required_skills:
            preview = obj.required_skills[:50]
            if len(obj.required_skills) > 50:
                preview += "..."
            return preview
        return "-"
    skills_preview.short_description = "Compétences"
