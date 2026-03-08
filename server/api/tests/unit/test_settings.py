from pathlib import Path
from django.test import TestCase
from django.conf import settings


class WhiteNoiseSettingsTest(TestCase):
    def test_whitenoise_in_middleware(self):
        self.assertIn(
            "whitenoise.middleware.WhiteNoiseMiddleware",
            settings.MIDDLEWARE,
        )

    def test_whitenoise_after_security_middleware(self):
        idx_security = settings.MIDDLEWARE.index(
            "django.middleware.security.SecurityMiddleware"
        )
        idx_whitenoise = settings.MIDDLEWARE.index(
            "whitenoise.middleware.WhiteNoiseMiddleware"
        )
        self.assertLess(idx_security, idx_whitenoise)

    def test_static_root_configured(self):
        self.assertIsInstance(settings.STATIC_ROOT, Path)
        self.assertEqual(settings.STATIC_ROOT.name, "staticfiles")

    def test_whitenoise_root_configured(self):
        self.assertIsInstance(settings.WHITENOISE_ROOT, Path)
        self.assertEqual(settings.WHITENOISE_ROOT.name, "static_build")
