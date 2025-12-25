from django.contrib import admin
from django.utils.html import format_html
from ats.recruiters.models.recuiters_model import Recruiter


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "user_display",          # Lien vers l'utilisateur associé
        "position",
        "phone",
        "company_logo_preview",  # Aperçu du logo
        "created",
    )
    list_filter = ("created", "position")
    search_fields = (
        "company_name",
        "user__email",           # Recherche par email de l'utilisateur lié
        "user__full_name",       # À adapter si ton User a full_name
        "phone",
    )
    readonly_fields = ("created", "company_logo_preview")
    date_hierarchy = "created"
    ordering = ("-created",)

    fieldsets = (
        ("Informations entreprise", {
            "fields": (
                "user",
                "company_name",
                "company_website",
                "company_description",
                "company_logo_url",
                "company_logo_preview",
            )
        }),
        ("Contact recruteur", {
            "fields": ("phone", "position"),
        }),
        ("Dates", {
            "fields": ("created",),
            "classes": ("collapse",),
        }),
    )

    # Affichage du nom/email de l'utilisateur lié
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.full_name or obj.user.email} ({obj.user.email})"
        return "-"
    user_display.short_description = "Utilisateur"
    user_display.admin_order_field = "user__email"

    # Aperçu du logo dans l'admin (très utile !)
    def company_logo_preview(self, obj):
        if obj.company_logo_url:
            return format_html(
                '<img src="{}" style="height: 80px; object-fit: contain; border-radius: 4px;" />',
                obj.company_logo_url
            )
        return "(Aucun logo)"
    company_logo_preview.short_description = "Aperçu logo"