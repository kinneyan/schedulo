from django.contrib import admin
from django.conf import settings
from django.http import FileResponse, Http404
from django.urls import include, path


def serve_react(request, path=""):
    index = settings.WHITENOISE_ROOT / "index.html"
    if not index.exists():
        raise Http404
    return FileResponse(index.open("rb"))


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", serve_react),
    path("<path:path>", serve_react),
]
