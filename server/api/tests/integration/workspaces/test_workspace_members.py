from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ....models import Workspace, WorkspaceMember, User, MemberPermissions


class AddMemberTests(APITestCase):
    """Integration tests for the add workspace member endpoint."""

    def setUp(self):
        """Create a workspace with an authenticated owner member and one additional user."""
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
        }
        self.user = User.objects.create_user(**self.user_data)

        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

        self.other_user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "0987654321",
        }
        self.other_user = User.objects.create_user(**self.other_user_data)

        self.workspace = Workspace.objects.create(created_by=self.user, owner=self.user)
        self.workspace_member = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, added_by=self.user
        )
        self.permission = MemberPermissions.objects.create(
            member=self.workspace_member,
            workspace=self.workspace,
            manage_workspace_members=True,
        )
        self.url = reverse(
            "workspace_members", kwargs={"workspace_id": self.workspace.id}
        )

    def test_add_workspace_member_permission(self):
        """Verify that a member with the manage_workspace_members permission can add a new member."""
        data = {"added_user_id": self.other_user.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_workspace_member_no_permission(self):
        """Verify that a member without manage_workspace_members permission is denied with a 403."""
        self.permission.manage_workspace_members = False
        self.permission.save()

        data = {"added_user_id": self.other_user.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"],
            "You do not have permission to add members to this workspace.",
        )

    def test_add_duplicate_workspace_member(self):
        """Verify that adding an already existing workspace member returns a 409 conflict."""
        data = {"added_user_id": self.other_user.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["error"]["message"],
            "User is already a member of this workspace.",
        )
