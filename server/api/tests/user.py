from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import User

class GetUserTests(APITestCase):
    def setUp(self):
        self.url = reverse('get_user')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_get_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['phone'], self.user.phone)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)

class UpdateUserTests(APITestCase):
    def setUp(self):
        self.url = reverse('get_user')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_update_user(self):
        update_data = {
            'email': 'updateduser@example.com',
            'password': 'newpassword',
            'current_password': 'testpassword',
            'phone': '0987654321',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.put(self.url, update_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Refresh the user instance to get the updated data
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, update_data['email'])
        self.assertTrue(self.user.check_password(update_data['password']))
        self.assertEqual(self.user.phone, update_data['phone'])
        self.assertEqual(self.user.first_name, update_data['first_name'])
        self.assertEqual(self.user.last_name, update_data['last_name'])

    def test_update_user_partial_data(self):
        update_data = {
            'email': 'partialupdate@example.com',
        }
        response = self.client.put(self.url, update_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Refresh the user instance to get the updated data
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, update_data['email'])
        self.assertEqual(self.user.phone, '1234567890')  # unchanged
        self.assertEqual(self.user.first_name, 'Test')  # unchanged
        self.assertEqual(self.user.last_name, 'User')  # unchanged

    def test_update_user_invalid_data(self):
        update_data = {
            'email': 'invalidemail',
        }
        response = self.client.put(self.url, update_data, format='json')
        self.assertEqual(response.status_code, 400)  # Assuming the view returns 400 for invalid data

    def test_update_user_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        update_data = {
            'email': 'unauthenticated@example.com',
        }
        response = self.client.put(self.url, update_data, format='json')
        self.assertEqual(response.status_code, 401)  # Assuming the view returns 401 for unauthenticated requests
