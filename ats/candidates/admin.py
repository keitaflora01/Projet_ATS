# ats/candidates/admin.py
from django.contrib import admin
from django.utils.html import format_html
from ats.candidates.models.candidates_model import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("user_display", "profile_photo_preview", "bio_preview")
    search_fields = ("user__email", "user__full_name", "bio")
    readonly_fields = ("bio_full", "profile_photo_preview")
    autocomplete_fields = ("user",)

    fieldsets = (
        ("Utilisateur associé", {"fields": ("user", "profile_photo")} ),
        ("Biographie", {"fields": ("bio", "bio_full")}),
    )

    def user_display(self, obj):
        if not obj.user:
            return "-"
        display_name = obj.user.get_full_name() or obj.user.email or "Anonyme"
        initial = display_name[0].upper() if display_name else "?"
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<div style="width: 40px; height: 40px; background: #007bff; color: white; border-radius: 50%; '
            'display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px;">{}</div>'
            '<div><strong>{}</strong><br><small style="color: #666;">{}</small></div>'
            '</div>',
            initial, display_name, obj.user.email
        )
    user_display.short_description = "Candidat"

    def bio_preview(self, obj):
        if obj.bio:
            preview = obj.bio.replace("\n", " ")[:100]
            if len(obj.bio) > 100:
                preview += " ..."
            return preview
        return "(Aucune biographie)"
    bio_preview.short_description = "Biographie (aperçu)"

    def bio_full(self, obj):
        if obj.bio:
            return format_html(
                '<div style="max-width: 800px; line-height: 1.6; white-space: pre-wrap; border-left: 4px solid #007bff; padding-left: 10px;">{}</div>',
                obj.bio
            )
        return format_html('<em style="color: #999;">Aucune biographie</em>')
    bio_full.short_description = "Biographie complète"

    def profile_photo_preview(self, obj):
        # Favorise la photo du profil liée au Candidate, sinon celle de l'utilisateur
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