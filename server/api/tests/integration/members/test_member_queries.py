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
    Shift,
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


class GetMemberShiftsTests(APITestCase):
    """Integration tests for the get member shifts endpoint."""

    def setUp(self):
        """Create a workspace with members, roles, and shifts."""
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
        self.user4 = User.objects.create_user(
            email="testuser4@example.com",
            password="testpassword",
            first_name="Test4",
            last_name="User4",
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

        self.member3 = WorkspaceMember.objects.create(
            user=self.user3, workspace=self.workspace, added_by=self.user
        )
        self.permissions3 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member3,
            is_owner=False,
            manage_workspace_members=False,
            manage_workspace_roles=False,
            manage_schedules=False,
            manage_time_off=False,
        )

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Test Role", pay_rate=15.00
        )

        self.shift1 = Shift.objects.create(
            workspace=self.workspace,
            member=self.member2,
            role=self.role,
            created_by=self.member,
            start_time="2026-01-01T09:00:00Z",
            end_time="2026-01-01T17:00:00Z",
        )
        self.shift2 = Shift.objects.create(
            workspace=self.workspace,
            member=self.member2,
            role=self.role,
            created_by=self.member,
            start_time="2026-01-02T09:00:00Z",
            end_time="2026-01-02T17:00:00Z",
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse("member_shifts", kwargs={"member_id": self.member2.id})

    def test_invalid_member(self):
        """Verify that a nonexistent member_id returns 404."""
        url = reverse("member_shifts", kwargs={"member_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_member_shifts_as_non_member(self):
        """Verify that a user who is not a workspace member receives 403."""
        self.client.force_authenticate(user=self.user4)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_member_shifts_without_permissions(self):
        """Verify that a member without manage permissions viewing another member's shifts receives 403."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_own_shifts_without_permissions(self):
        """Verify that a member without manage permissions can retrieve their own shifts."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(len(result), 2)

    def test_get_member_shifts_as_owner(self):
        """Verify that an owner can retrieve another member's shifts with correct structure."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(len(result), 2)

        expected_shift1 = {
            "id": self.shift1.id,
            "role": {"id": self.role.id, "name": self.role.name},
            "start_time": self.shift1.start_time,
            "end_time": self.shift1.end_time,
        }
        expected_shift2 = {
            "id": self.shift2.id,
            "role": {"id": self.role.id, "name": self.role.name},
            "start_time": self.shift2.start_time,
            "end_time": self.shift2.end_time,
        }

        self.assertEqual(result[0], expected_shift1)
        self.assertEqual(result[1], expected_shift2)

    def test_get_member_shifts_empty(self):
        """Verify that an empty list is returned when the member has no shifts."""
        Shift.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["result"]), 0)
