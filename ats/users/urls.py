from django.urls import path
from ats.users.api.views import RegisterView, UserProfileView, LogoutView, LoginView
from ats.users.api.views.testimonial_views import TestimonialDetailView, TestimonialListCreateView
from ats.users.api.views.user_views import UserDetailView, UserListView

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/profile/", UserProfileView.as_view(), name="profile"),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/users/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    
    path('api/testimonials/', TestimonialListCreateView.as_view(), name='testimonial-list-create'),
    path('api/testimonials/<uuid:id>/', TestimonialDetailView.as_view(), name='testimonial-detail'),
]