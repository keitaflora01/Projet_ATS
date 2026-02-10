from django.contrib import admin
from django.utils.html import format_html
from ats.recruiters.models.recruiters_model import  RecruiterProfile


@admin.register(RecruiterProfile)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "user_display",
        "profile_photo_preview",
        "position",
        "phone",
        "company_logo_preview",
        "created",
    )
    list_filter = ("created", "position")
    search_fields = (
        "company_name",
        "user__email",        
        "user__full_name",       
        "phone",
    )
    readonly_fields = ("created", "company_logo_preview", "profile_photo_preview")
    date_hierarchy = "created"
    ordering = ("-created",)

    fieldsets = (
        ("Informations entreprise", {
            "fields": (
                "user",
                "profile_photo",
                "company_name",
                "company_website",
                "company_description",
                "company_logo_file",
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

    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.full_name or obj.user.email} ({obj.user.email})"
        return "-"
    user_display.short_description = "Utilisateur"
    user_display.admin_order_field = "user__email"

    def company_logo_preview(self, obj):
        if obj.company_logo_file:
            return format_html(
                '<img src="{}" style="height: 80px; object-fit: contain; border-radius: 4px;" />',
                obj.company_logo_file
            )
        return "(Aucun logo)"
    company_logo_preview.short_description = "Aperçu logo"

    def profile_photo_preview(self, obj):
        # Use recruiter profile photo if present, otherwise user's
        img = None
        if getattr(obj, "profile_photo", None):
            img = obj.profile_photo
        elif getattr(obj.user, "profile_photo", None):
            img = obj.user.profile_photo

        if img:
            return format_html(
                '<img src="{}" style="height: 60px; width:60px; object-fit:cover; border-radius:50%;" />',
                img.url,
            )
        return "(Aucune photo)"
    profile_photo_preview.short_description = "Photo profil"