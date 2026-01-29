# ats/jobs/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg
from .models.jobs_model import JobOffer, JobType, ContractType


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
        "pass_percentage_colored",   # ← COLONNE PASS % AVEC COULEUR
        "skills_preview",
        "ai_score_avg",
        "candidate_count",
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

    def recruiter_display(self, obj):
        return obj.recruiter.company_name if obj.recruiter else "-"
    recruiter_display.short_description = "Entreprise"
    recruiter_display.admin_order_field = "recruiter__company_name"

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
            '<span style="background:{}; color:white; padding:4px 8px; border-radius:4px;">{}</span>',
            color, text
        )
    job_type_badge.short_description = "Type"

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
            '<span style="background:{}; color:white; padding:4px 8px; border-radius:4px;">{}</span>',
            color, text
        )
    contract_type_badge.short_description = "Contrat"

    def remote_badge(self, obj):
        if obj.is_remote:
            return format_html('<span style="color:green;">✓ Remote</span>')
        return format_html('<span style="color:gray;">Bureau</span>')
    remote_badge.short_description = "Remote"

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">● Active</span>')
        return format_html('<span style="color:red;">● Inactive</span>')
    active_badge.short_description = "Active"

    def salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_min} – {obj.salary_max} €"
        elif obj.salary_min:
            return f"≥ {obj.salary_min} €"
        elif obj.salary_max:
            return f"≤ {obj.salary_max} €"
        return "-"
    salary_range.short_description = "Salaire"

    def skills_preview(self, obj):
        if obj.required_skills:
            preview = obj.required_skills[:50]
            return preview + "..." if len(obj.required_skills) > 50 else preview
        return "-"
    skills_preview.short_description = "Compétences"

    def candidate_count(self, obj):
        return obj.submissions.count()
    candidate_count.short_description = "Candidatures"

    def ai_score_avg(self, obj):
        avg_score = obj.submissions.aggregate(avg=Avg('application__ia_score'))['avg']
        if avg_score is None:
            return format_html('<span style="color:gray;">Aucune</span>')
        # cast to float to avoid formatting errors if DB returns Decimal or SafeString
        try:
            avg_val = float(avg_score)
        except Exception:
            avg_val = 0.0
        color = "green" if avg_val >= 70 else "orange" if avg_val >= 50 else "red"
        # format the numeric value into a string first — format_html escapes args
        formatted_score = f"{avg_val:.1f}"
        return format_html('<strong style="color:{};">{} / 100</strong>', color, formatted_score)
    ai_score_avg.short_description = "Score IA moyen"

    # NOUVELLE MÉTHODE : affichage coloré de pass_percentage
    def pass_percentage_colored(self, obj):
        # ensure percent is numeric (DB may return Decimal or string-like)
        try:
            percent_val = int(obj.pass_percentage)
        except Exception:
            try:
                percent_val = int(float(obj.pass_percentage))
            except Exception:
                percent_val = 0
        color = "green" if percent_val >= 80 else "orange" if percent_val >= 50 else "red"
        return format_html('<strong style="color:{};">{} %</strong>', color, percent_val)
    pass_percentage_colored.short_description = "Pass %"
    pass_percentage_colored.admin_order_field = "pass_percentage"

    fieldsets = (
        ("Informations principales", {
            "fields": ("recruiter", "title", "description", ("job_type", "contract_type"), "location", ("is_remote", "is_active")),
        }),
        ("Critères de sélection", {
            "fields": ("pass_percentage", ("salary_min", "salary_max")),
        }),
        ("Expiration & Publication", {
            "fields": ("expires_at", "published_at", "is_expired"),
        }),
        ("Contenu détaillé", {
            "fields": ("required_skills", "requirements"),
            "classes": ("collapse",),
        }),
    )