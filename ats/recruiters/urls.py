from django.urls import path
from .api.views.recruiters_views import RecruiterListView, RecruiterDetailView

urlpatterns = [
    path("api/recruiters/", RecruiterListView.as_view(), name="recruiter-list"),
    path("api/recruiters/<uuid:id>/", RecruiterDetailView.as_view(), name="recruiter-detail"),
]