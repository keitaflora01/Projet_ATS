# ats/candidates/admin.py
from django.contrib import admin
from django.utils.html import format_html
from ats.candidates.models.candidates_model import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "user_display",              # Nom / Email + photo si disponible
        "phone",
        "location",
        "years_of_experience",
        "desired_salary_display",
        "availability_date",
        "resume_link",               # Lien direct vers le CV
        "created",
    )
    list_filter = (
        "years_of_experience",
        "availability_date",
        "location",
        "created",
    )
    search_fields = (
        "user__email",
        "user__full_name",           # À adapter si ton User a un champ full_name
        "phone",
        "location",
    )
    readonly_fields = (
        "created",
        "profile_picture_preview",
        "resume_preview",
    )
    date_hierarchy = "created"
    ordering = ("-created",)
    autocomplete_fields = ("user",)  # Très pratique pour associer un utilisateur existant

    fieldsets = (
        ("Utilisateur & Contact", {
            "fields": (
                "user",
                "phone",
                "location",
            )
        }),
        ("Profil", {
            "fields": (
                "bio",
                "years_of_experience",
                "desired_salary",
                "availability_date",
            )
        }),
        ("Fichiers", {
            "fields": (
                "profile_picture_url",
                "profile_picture_preview",
                "resume_url",
                "resume_preview",
            )
        }),
        ("Dates", {
            "fields": ("created",),
            "classes": ("collapse",),
        }),
    )

    # Affichage riche de l'utilisateur avec photo si disponible
    def user_display(self, obj):
        if not obj.user:
            return "-"
        
        display_name = obj.user.full_name or obj.user.email or "Inconnu"
        
        if obj.profile_picture_url:
            return format_html(
                '<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; vertical-align: middle; margin-right: 8px;" /> {}',
                obj.profile_picture_url, display_name
            )
        else:
            return format_html(
                '<span style="display: inline-block; width: 32px; height: 32px; background: #ccc; border-radius: 50%; text-align: center; line-height: 32px; margin-right: 8px; color: white; font-weight: bold;">{}</span> {}',
                display_name[0].upper() if display_name else "?",
                display_name
            )
    user_display.short_description = "Candidat"
    user_display.admin_order_field = "user__email"

    # Aperçu de la photo de profil dans le formulaire
    def profile_picture_preview(self, obj):
        if obj.profile_picture_url:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 8px;" />',
                obj.profile_picture_url
            )
        return "(Aucune photo)"
    profile_picture_preview.short_description = "Aperçu photo"

    # Lien cliquable vers le CV
    def resume_link(self, obj):
        if obj.resume_url:
            return format_html('<a href="{}" target="_blank">📄 Voir le CV</a>', obj.resume_url)
        return "(Aucun CV)"
    resume_link.short_description = "CV"

    # Aperçu du CV (lien dans le formulaire aussi)
    def resume_preview(self, obj):
        if obj.resume_url:
            return format_html('<a href="{}" target="_blank">🔗 Ouvrir le CV (nouvel onglet)</a>', obj.resume_url)
        return "(Aucun CV téléchargé)"
    resume_preview.short_description = "CV"

    # Salaire souhaité lisible
    def desired_salary_display(self, obj):
        if obj.desired_salary:
            return f"{obj.desired_salary} €"
        return "Non renseigné"
    desired_salary_display.short_description = "Salaire souhaité"