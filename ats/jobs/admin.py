from django.contrib import admin
from django.utils.html import format_html
from ats.jobs.models.jobs_model import JobOffer  


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recruiter_display",     
        "job_type",
        "location",
        "remote_badge",           
        "active_badge",         
        "salary_range",           
        "published_at",
    )
    list_filter = (
        "job_type",
        "is_remote",
        "is_active",
        "location",
        "published_at",
    )
    search_fields = (
        "title",
        "location",
        "description",
        "recruiter__company_name",   
        "recruiter__user__email",
    )
    readonly_fields = ("published_at",)
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    autocomplete_fields = ("recruiter",)  

    fieldsets = (
        ("Informations principales", {
            "fields": (
                "recruiter",
                "title",
                "description",
                "job_type",
                "location",
                ("is_remote", "is_active"),
            )
        }),
        ("Contenu détaillé", {
            "fields": (
                "requirements",
                "responsibilities",
            ),
            "classes": ("collapse",),  # Pliée par défaut
        }),
        ("Salaire & Expiration", {
            "fields": (
                ("salary_min", "salary_max"),
                "expires_at",
            )
        }),
        ("Dates", {
            "fields": ("published_at",),
            "classes": ("collapse",),
        }),
    )

    # Affichage lisible du recruteur
    def recruiter_display(self, obj):
        if obj.recruiter:
            return f"{obj.recruiter.company_name} ({obj.recruiter.user.email})"
        return "-"
    recruiter_display.short_description = "Recruteur"
    recruiter_display.admin_order_field = "recruiter__company_name"

    # Badge pour remote
    def remote_badge(self, obj):
        if obj.is_remote:
            return format_html('<span style="color: green; font-weight: bold;">✓ Remote</span>')
        return format_html('<span style="color: gray;">Office</span>')
    remote_badge.short_description = "Remote"
    remote_badge.admin_order_field = "is_remote"

    # Badge pour actif/inactif
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: red;">● Inactive</span>')
    active_badge.short_description = "Active"
    active_badge.admin_order_field = "is_active"

    def salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_min} – {obj.salary_max} €"
        elif obj.salary_min:
            return f"À partir de {obj.salary_min} €"
        elif obj.salary_max:
            return f"Jusqu’à {obj.salary_max} €"
        return "Non communiqué"
    salary_range.short_description = "Salaire"