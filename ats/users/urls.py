from django.urls import path
from ats.users.api.views import RegisterView, UserProfileView, LogoutView, LoginView
from ats.users.api.views.testimonial_views import TestimonialDetailView, TestimonialListCreateView

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/profile/", UserProfileView.as_view(), name="profile"),
    
    path('api/testimonials/', TestimonialListCreateView.as_view(), name='testimonial-list-create'),
    path('api/testimonials/<uuid:id>/', TestimonialDetailView.as_view(), name='testimonial-detail'),
]