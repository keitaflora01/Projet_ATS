"""
Minimal view stubs for the `users` app.

This file is intentionally minimal — replace these with API endpoints
or DRF viewsets when you implement your own user routes.
"""

# For an API-only backend you will probably want to use Django REST Framework
# viewsets/serializers here. Keep this file as a reference placeholder.

from django.http import JsonResponse


def placeholder(request):
    return JsonResponse({"detail": "Implement user endpoints here."})
