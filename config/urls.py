from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Users & Auth
    path("users/", include("ats.users.urls", namespace="users")),

    # API Documentation (Swagger)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Redirection de la page d'accueil vers Swagger
    path("", RedirectView.as_view(url="/api/docs/", permanent=False), name="home"),

    # Apps de ton ATS
    path("jobs/", include("ats.jobs.urls")),
    path("applications/", include("ats.applications.urls")),
    path("candidates/", include("ats.candidates.urls")),
    path("recruiters/", include("ats.recruiters.urls")),
    path("interviews/", include("ats.interviews.urls")),        # je recommande de simplifier
    path("submissions/", include("ats.submissions.urls")),
]

# Media files en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Pages d'erreur pour le développement
    from django.views import defaults as default_views
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]

    # Debug Toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns