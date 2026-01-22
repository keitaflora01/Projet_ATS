"""Django admin configuration for users app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from ats.candidates.models.candidates_model import Candidate
from ats.recruiters.models.recruiters_model import RecruiterProfile
from .models.user_model import User, UserRole
from .models.service_model import Service
from .models.testimonial_model import Testimonial
from .models.policy_model import Policy
from .models.statistic_model import Statistic


class CandidateInline(admin.StackedInline):
    model = Candidate
    can_delete = False
    verbose_name_plural = "Profil candidat"
    readonly_fields = ("created", "modified")


class RecruiterProfileInline(admin.StackedInline):
    model = RecruiterProfile
    can_delete = False
    verbose_name_plural = "Profil recruteur"
    readonly_fields = ("created", "modified")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "role", "is_active", "is_verified", "created")
    list_filter = ("is_active", "is_verified", "role")
    search_fields = ("email", "full_name")
    ordering = ("-created",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("full_name", "role")}),
        ("Permissions", {"fields": ("is_active", "is_verified", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2", "role", "is_active", "is_verified")}
        ),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        inlines = super().get_inline_instances(request, obj)
        if obj.role == UserRole.CANDIDATE:
            inlines.append(CandidateInline(self.model, self.admin_site))
        elif obj.role == UserRole.RECRUITER:
            inlines.append(RecruiterProfileInline(self.model, self.admin_site))
        return inlines


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "target", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "user_link",
        "short_message",
        "rating_stars",
        "approved_badge",
        "order",
        "created",
    )
    list_filter = ("is_approved", "rating", "created")
    search_fields = ("user__email", "user__full_name", "message")
    # Keep only fields that are safe to edit inline. 'is_approved' can be edited
    # in the change form to avoid admin.E122 checks related to list_editable.
    list_editable = ("order",)
    ordering = ("-created",)
    actions = ["approve_selected", "reject_selected"]

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/">{} ({})</a>',
            obj.user.id,
            obj.user.get_full_name() or obj.user.email,
            obj.user.email
        )
    user_link.short_description = "Utilisateur"

    def short_message(self, obj):
        return obj.message[:80] + "..." if len(obj.message) > 80 else obj.message
    short_message.short_description = "Message (aperçu)"

    def rating_stars(self, obj):
        return format_html('⭐' * obj.rating)
    rating_stars.short_description = "Note"

    def approved_badge(self, obj):
        if obj.is_approved:
            return format_html('<span style="color:green; font-weight:bold;">✔ Approuvé</span>')
        return format_html('<span style="color:orange;">⌛ En attente</span>')
    approved_badge.short_description = "Statut"

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} avis approuvés.")
    approve_selected.short_description = "Approuver les avis sélectionnés"

    def reject_selected(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} avis rejetés.")
    reject_selected.short_description = "Rejeter les avis sélectionnés"

    fieldsets = (
        ("Informations", {"fields": ("user", "message", "rating")}),
        ("Modération & Ordre", {"fields": ("is_approved", "order")}),
        ("Dates", {"fields": ("created", "modified"), "classes": ("collapse",)}),
    )


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "is_active")
    search_fields = ("slug", "title")


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "is_dynamic")