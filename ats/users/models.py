"""
Minimal `User` model placeholder.

This file has been reduced to a minimal, working placeholder so you can
re-implement your own custom user model, routes and logic. Keep or replace
this class according to your needs.

If you want to use the default Django user model for now, you can delete
this class and set ``AUTH_USER_MODEL`` to ``"auth.User"`` in settings.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Minimal placeholder user.

    Add fields and methods here when you implement your own user model.
    """
    pass
