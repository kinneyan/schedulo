from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ....models import User


class RegisterTests(APITestCase):
    """Integration tests for the registration endpoint."""

    def setUp(self):
        """Create a test user and set the registration URL."""
        self.url = reverse("register")
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_valid(self):
        """Verify that valid registration data returns 201 with access and refresh tokens."""
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "0987654321",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_email_exists(self):
        """Verify that a duplicate email returns 409 with an error message."""
        data = self.user_data
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error"]["code"], 409)
        self.assertEqual(
            response.data["error"]["message"], "Account with this email already exists"
        )

    def test_register_invalid_data(self):
        """Verify that invalid field values return 400 with an error message."""
        data = {
            "email": "invalidemail",
            "password": "short",
            "first_name": "",
            "last_name": "",
            "phone": "",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], 400)
        self.assertEqual(response.data["error"]["message"], "Invalid request data")
