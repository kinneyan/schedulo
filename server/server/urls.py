from django.contrib import admin
from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest
from django.urls import include, path


def serve_react(request: HttpRequest, path: str = "") -> FileResponse:
    index = settings.WHITENOISE_ROOT / "index.html"
    try:
        return FileResponse(index.open("rb"))
    except FileNotFoundError:
        raise Http404


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", serve_react),
    path("<path:path>", serve_react),
]
