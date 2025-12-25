from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.user_model import User, UserRole
from .models.service_model import Service
from .models.testimonial_model import Testimonial
from .models.policy_model import Policy
# from .models.contact_model import ContactInfo, ContactMessage
from .models.statistic_model import Statistic

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

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "target", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "rating", "is_approved", "created")
    list_filter = ("is_approved", "rating")

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "is_active")
    search_fields = ("slug", "title")

# @admin.register(ContactInfo)
# class ContactInfoAdmin(admin.ModelAdmin):
#     def has_add_permission(self, request):
#         return False  # Une seule entrée
#     def has_delete_permission(self, request, obj=None):
#         return False

# @admin.register(ContactMessage)
# class ContactMessageAdmin(admin.ModelAdmin):
#     list_display = ("name", "email", "subject", "is_read", "created_at")
#     list_filter = ("is_read",)
#     actions = ["mark_as_read"]

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lu"

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "is_dynamic")