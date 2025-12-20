# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views import defaults as default_views

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Media files en développement
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# Pages d'erreur personnalisées en DEBUG
if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]

    # Django Debug Toolbar (si installé)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

# Tu pourras ajouter plus tard tes propres URLs ici, par exemple :
# path("", include("ats.jobs.urls")),
# path("accounts/", include("allauth.urls")),