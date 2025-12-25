from django.urls import path
from ats.users.api.views import RegisterView, UserProfileView, LogoutView, LoginView

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/profile/", UserProfileView.as_view(), name="profile"),
]