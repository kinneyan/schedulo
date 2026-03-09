"""URL configuration for the server project."""

from django.contrib import admin
from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest
from django.urls import include, path


def serve_react(request: HttpRequest, path: str = "") -> FileResponse:
    """Serve the React app's index.html for all non-API routes.

    :param HttpRequest request: The incoming HTTP request.
    :param str path: The URL path captured by the catch-all pattern.
    :return: The React app's index.html as a file response.
    :rtype: FileResponse
    :raises Http404: If the built index.html does not exist.
    """
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
