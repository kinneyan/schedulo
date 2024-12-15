from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Workspace, WorkspaceMember, User, MemberPermissions

class AddMemberTests(APITestCase):
    def setUp(self):
        self.url = reverse("add_workspace_member")

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

        self.other_user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "0987654321"
        }
        self.other_user = User.objects.create_user(**self.other_user_data)

        # add workspace
        self.workspace = Workspace.objects.create(created_by_id=self.user, owner_id=self.user)
        self.workspace_member = WorkspaceMember.objects.create(user_id=self.user, workspace_id=self.workspace, added_by_id=self.user)
        self.permission = MemberPermissions.objects.create(member_id=self.workspace_member, workspace_id=self.workspace, MANAGE_WORKSPACE_MEMBERS=True)

    def test_add_workspace_member_permission(self):
        data = {
            'added_user_id': self.other_user.id,
            'workspace_id': self.workspace.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_workspace_member_no_permission(self):
        self.permission.MANAGE_WORKSPACE_MEMBERS = False
        self.permission.save()
        data = {
            'added_user_id': self.other_user.id,
            'workspace_id': self.workspace.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "You do not have permission to add members to this workspace")

