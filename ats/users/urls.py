"""URLs for users app (placeholder).

Replace with API endpoints / DRF routers when implementing user routes.
"""

from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("placeholder/", views.placeholder, name="placeholder"),
]
