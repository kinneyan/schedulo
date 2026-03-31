"""Shared utility functions for the server project."""

import os

from django.core.exceptions import ImproperlyConfigured


def require_env(name: str) -> str:
    """Return the value of a required environment variable.

    :param str name: The name of the environment variable.
    :return: The value of the environment variable.
    :rtype: str
    :raises ImproperlyConfigured: If the variable is not set or empty.
    """
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"Required environment variable '{name}' is not set.")
    return value
