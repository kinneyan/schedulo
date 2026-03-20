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


class GetMemberTests(APITestCase):
    """Integration tests for the get member endpoint."""

    def setUp(self):
        """Create a workspace with members and roles."""
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

        self.role1 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Test Role 1", pay_rate=15.00
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Test Role 2", pay_rate=20.00
        )

        self.member_role1 = MemberRole.objects.create(
            member=self.member2, workspace_role=self.role1
        )
        self.member_role2 = MemberRole.objects.create(
            member=self.member2, workspace_role=self.role2
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse("member", kwargs={"member_id": self.member2.id})

    def test_invalid_member(self):
        """Verify that a nonexistent member_id returns 404."""
        url = reverse("member", kwargs={"member_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_member_as_non_member(self):
        """Verify that a user who does not share a workspace with the member receives 403."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_member_valid(self):
        """Verify that a workspace member can retrieve another member's details with correct structure."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(result["id"], self.user2.id)
        self.assertEqual(result["first_name"], self.user2.first_name)
        self.assertEqual(result["last_name"], self.user2.last_name)
        self.assertEqual(len(result["member_roles"]), 2)
        self.assertEqual(
            result["member_roles"][0], {"id": self.role1.id, "name": self.role1.name}
        )
        self.assertEqual(
            result["member_roles"][1], {"id": self.role2.id, "name": self.role2.name}
        )

    def test_get_member_no_roles(self):
        """Verify that a member with no assigned roles returns an empty member_roles list."""
        url = reverse("member", kwargs={"member_id": self.member.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"]["member_roles"], [])

    def test_get_member_as_unprivileged_member(self):
        """Verify that a member without manage permissions can still retrieve another member's details."""
        self.client.force_authenticate(user=self.user2)
        url = reverse("member", kwargs={"member_id": self.member.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteMemberTests(APITestCase):
    """Integration tests for the delete member endpoint."""

    def setUp(self):
        """Create a workspace with members."""
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

        self.client.force_authenticate(user=self.user)
        self.url = reverse("member", kwargs={"member_id": self.member2.id})

    def test_invalid_member(self):
        """Verify that a nonexistent member_id returns 404."""
        url = reverse("member", kwargs={"member_id": 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_member_as_non_member(self):
        """Verify that a user who is not a workspace member receives 403."""
        self.client.force_authenticate(user=self.user4)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_member_without_permissions(self):
        """Verify that a member without manage permissions cannot delete another member."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(WorkspaceMember.objects.filter(pk=self.member2.id).exists())

    def test_delete_member_as_owner(self):
        """Verify that an owner can delete another member and the member no longer exists."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(WorkspaceMember.objects.filter(pk=self.member2.id).exists())

    def test_delete_own_membership(self):
        """Verify that a member without manage permissions can delete their own membership."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(WorkspaceMember.objects.filter(pk=self.member2.id).exists())
