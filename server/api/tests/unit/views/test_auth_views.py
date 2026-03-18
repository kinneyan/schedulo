from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from ....views.auth import Register


class RegisterViewTest(TestCase):
    """Test cases for Register view business logic"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = Register()
        self.view.request = None

    def _create_drf_request(self, url, data):
        request = self.factory.post(url, data, format="json")
        self.view.setup(request)
        return self.view.initialize_request(request)

    @patch("api.views.auth.RegisterUserSerializer")
    @patch("api.views.auth.User.objects.create_user")
    def test_register_internal_server_error(
        self, mock_create_user, mock_register_serializer
    ):
        """Verify that an unexpected exception during user creation returns 500."""
        mock_register_instance = MagicMock()
        mock_register_instance.is_valid.return_value = True
        mock_register_instance.validated_data = {
            "email": "test@example.com",
            "password": "password",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
        }
        mock_register_serializer.return_value = mock_register_instance
        mock_create_user.side_effect = Exception("Database error")

        request = self._create_drf_request(
            "/register/",
            {
                "email": "test@example.com",
                "password": "password",
                "first_name": "Test",
                "last_name": "User",
                "phone": "1234567890",
            },
        )
        response = self.view.post(request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"]["code"], 500)
        self.assertEqual(response.data["error"]["message"], "Internal server error")
