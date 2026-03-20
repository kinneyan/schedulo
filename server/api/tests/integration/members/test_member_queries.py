from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ....models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
)


class GetMemberPermissionsTests(APITestCase):
    """Integration tests for the get member permissions endpoint."""

    def setUp(self):
        """Create a workspace with two members and an outside user."""
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            phone="1234567890",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="testpassword",
            first_name="Test2",
            last_name="User2",
            phone="1234567890",
        )
        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpassword",
            first_name="Test3",
            last_name="User3",
            phone="1234567890",
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace, added_by=self.user
        )
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            is_owner=False,
            manage_workspace_members=False,
            manage_workspace_roles=False,
            manage_schedules=False,
            manage_time_off=False,
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse("member_permissions", kwargs={"member_id": self.member.id})

    def test_invalid_member(self):
        """Verify that a nonexistent member_id returns 404."""
        url = reverse("member_permissions", kwargs={"member_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_permissions_as_non_member(self):
        """Verify that a user who does not share a workspace with the member receives 403."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_own_permissions(self):
        """Verify that a member can retrieve their own permissions with correct values."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(result["is_owner"], self.permissions.is_owner)
        self.assertEqual(
            result["manage_workspace_members"],
            self.permissions.manage_workspace_members,
        )
        self.assertEqual(
            result["manage_workspace_roles"], self.permissions.manage_workspace_roles
        )
        self.assertEqual(result["manage_schedules"], self.permissions.manage_schedules)
        self.assertEqual(result["manage_time_off"], self.permissions.manage_time_off)

    def test_get_other_member_permissions(self):
        """Verify that a member can retrieve another member's permissions from the same workspace."""
        url = reverse("member_permissions", kwargs={"member_id": self.member2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(result["is_owner"], self.permissions2.is_owner)
        self.assertEqual(
            result["manage_workspace_members"],
            self.permissions2.manage_workspace_members,
        )
        self.assertEqual(
            result["manage_workspace_roles"], self.permissions2.manage_workspace_roles
        )
        self.assertEqual(result["manage_schedules"], self.permissions2.manage_schedules)
        self.assertEqual(result["manage_time_off"], self.permissions2.manage_time_off)
