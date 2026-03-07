from pathlib import Path
from unittest.mock import mock_open, patch

from django.test import TestCase, override_settings


@override_settings(WHITENOISE_ROOT=Path("/fake/static_build"))
class CatchAllURLTest(TestCase):
    @patch("pathlib.Path.exists", return_value=True)
    @patch(
        "pathlib.Path.open",
        mock_open(read_data=b"<html><div id='root'></div></html>"),
    )
    def test_unknown_path_returns_200(self, _exists):
        response = self.client.get("/some-react-route/")
        self.assertEqual(response.status_code, 200)

    @patch("pathlib.Path.exists", return_value=True)
    @patch(
        "pathlib.Path.open",
        mock_open(read_data=b"<html><div id='root'></div></html>"),
    )
    def test_nested_react_route_returns_200(self, _exists):
        response = self.client.get("/some-react-route/nested/path/")
        self.assertEqual(response.status_code, 200)

    def test_api_routes_not_caught(self):
        response = self.client.get("/api/nonexistent/")
        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn(b"<div id='root'>", response.content)

    def test_admin_routes_not_caught(self):
        response = self.client.get("/admin/")
        self.assertNotIn(b"<div id='root'>", response.content)
