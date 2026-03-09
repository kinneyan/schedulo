import os
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from server.utils import require_env


class RequireEnvTest(TestCase):
    @patch.dict(os.environ, {"MY_VAR": "hello"})
    def test_returns_value_when_set(self):
        self.assertEqual(require_env("MY_VAR"), "hello")

    @patch.dict(os.environ, {}, clear=True)
    def test_raises_when_missing(self):
        os.environ.pop("MY_VAR", None)
        with self.assertRaises(ImproperlyConfigured) as ctx:
            require_env("MY_VAR")
        self.assertIn("MY_VAR", str(ctx.exception))

    @patch.dict(os.environ, {"MY_VAR": ""})
    def test_raises_when_empty(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            require_env("MY_VAR")
        self.assertIn("MY_VAR", str(ctx.exception))
