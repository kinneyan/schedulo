from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import User


class TestLogin(APITestCase):
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
