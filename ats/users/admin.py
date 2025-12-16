"""Admin registration for the `users` app - minimal.

This registers the placeholder User model with the Django admin using the
default ModelAdmin. Replace with custom admin/forms when you implement your
own user model.
"""

from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_staff", "is_superuser")
    search_fields = ("username",)
