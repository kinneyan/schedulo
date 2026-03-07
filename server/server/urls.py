from django.contrib import admin
from django.conf import settings
from django.http import FileResponse, Http404
from django.urls import include, path, re_path


def serve_react(request):
    index = settings.WHITENOISE_ROOT / "index.html"
    if not index.exists():
        raise Http404
    return FileResponse(index.open("rb"))


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    re_path(r"^(?!api/|admin/).*$", serve_react),
]
