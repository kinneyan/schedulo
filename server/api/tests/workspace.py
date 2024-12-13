from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Workspace, WorkspaceMember, User

class AddMemberTests(APITestCase):
    def setUp(self):
        self.url = reverse("create_workspace")

        # add users
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        self.user = User.objects.create_user(**self.user_data)

        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "0987654321"
        }
        other_user = User.objects.create_user(**data)

        # add workspace
        data = {
            # put workspace name, ect here once added
        }
        response = self.client.post(self.url, data, format='json')

        self.url = reverse("add_workspace_member")

    def test_add_valid(self):
        data = {
            "pay_rate": 15,
            "added_user_id": 2,
            "workspace_id": 1
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkspaceMember.objects.filter(user_id=User.objects.get(pk=data['added_user_id']), workspace_id=Workspace.objects.get(pk=data['workspace_id'])).exists())

    def test_add_duplicate(self):
        data = {
            "pay_rate": 15,
            "added_user_id": 2,
            "workspace_id": 1
        }
        response = self.client.post(self.url, data, format='json')
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

