from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import User


class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(email='test@example.com', password='password123')

    def test_login_with_valid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error']['code'], 401)
        self.assertEqual(response.data['error']['message'], 'Incorrect email or password')

    def test_login_with_invalid_request_data(self):
        data = {
            'email': 'test@example.com'
            # Missing password
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error']['code'], 400)
        self.assertEqual(response.data['error']['message'], 'Invalid request data')

class RegisterTests(APITestCase):
    
    def setUp(self):
        self.url = reverse('register')
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_valid(self):
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "0987654321"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_email_exists(self):
        data = self.user_data
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error"]["code"], 409)
        self.assertEqual(response.data["error"]["message"], "Account with this email already exists")

    def test_register_invalid_data(self):
        data = {
            "email": "invalidemail",
            "password": "short",
            "first_name": "",
            "last_name": "",
            "phone": ""
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], 400)
        self.assertEqual(response.data["error"]["message"], "Invalid request data")
