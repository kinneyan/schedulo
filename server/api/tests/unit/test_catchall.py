from pathlib import Path
from unittest.mock import mock_open, patch

from django.test import TestCase, override_settings


@override_settings(WHITENOISE_ROOT=Path("/fake/static_build"))
class CatchAllURLTest(TestCase):
    @patch("pathlib.Path.open", mock_open(read_data=b"<html><div id='root'></div></html>"))
    def test_root_path_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @patch("pathlib.Path.open", mock_open(read_data=b"<html><div id='root'></div></html>"))
    def test_subroute_returns_200(self):
        response = self.client.get("/some-react-route/nested/path/")
        self.assertEqual(response.status_code, 200)

    @patch("pathlib.Path.open", side_effect=FileNotFoundError)
    def test_missing_index_returns_404(self, _open):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)

    def test_api_routes_not_caught(self):
        response = self.client.get("/api/nonexistent/")
        self.assertEqual(response.status_code, 404)

    def test_admin_routes_not_caught(self):
        response = self.client.get("/admin/")
        self.assertNotIn(b"<div id='root'>", response.content)
