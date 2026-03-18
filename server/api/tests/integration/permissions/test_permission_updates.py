from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ....models import MemberPermissions, WorkspaceMember, Workspace, User


class UpdatePermissionsTests(APITestCase):
    """Integration tests for the member permissions update endpoint."""

    def setUp(self):
        """Create a workspace, owner, member, and initial permissions."""
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
        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)
        self.member = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            is_owner=False,
            manage_workspace_members=True,
            manage_workspace_roles=False,
            manage_schedules=False,
            manage_time_off=False,
        )
        self.client.force_authenticate(user=self.member.user)
        self.url = reverse("member_permissions", kwargs={"member_id": self.member.id})

    def test_member_not_found(self):
        """Verify that a non-existent member_id returns a 404 error."""
        url = reverse("member_permissions", kwargs={"member_id": 999})
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"]["message"], "Could not find member with provided ID."
        )

    def test_create_new_permissions(self):
        """Verify that a permissions record is created when one does not yet exist."""
        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            MemberPermissions.objects.filter(
                workspace_id=self.workspace.id, member_id=self.member
            ).exists()
        )

    def test_cannot_update_owner_permissions(self):
        """Verify that attempting to update a workspace owner's permissions returns 409."""
        self.permissions.is_owner = True
        self.permissions.save()
        response = self.client.put(
            self.url,
            {"manage_workspace_members": True},
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["error"]["message"],
            "Cannot update permissions for workspace owner.",
        )

    def test_successfully_update_permissions(self):
        """Verify that all permission flags are correctly updated on success."""
        data = {
            "manage_workspace_members": True,
            "manage_workspace_roles": True,
            "manage_schedules": True,
            "manage_time_off": True,
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.permissions.refresh_from_db()
        self.assertTrue(self.permissions.manage_workspace_members)
        self.assertTrue(self.permissions.manage_workspace_roles)
        self.assertTrue(self.permissions.manage_schedules)
        self.assertTrue(self.permissions.manage_time_off)

    def test_member_not_in_workspace(self):
        """Verify that updating permissions for a member in a different workspace returns 403."""
        new_workspace = Workspace.objects.create(owner=self.user, created_by=self.user)
        new_member = WorkspaceMember.objects.create(
            user=self.user2, workspace=new_workspace, added_by=self.user
        )

        url = reverse("member_permissions", kwargs={"member_id": new_member.id})
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_workspace_isolation(self):
        """Verify that a privileged member of another workspace cannot update permissions in this workspace."""
        user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpassword",
            first_name="Test3",
            last_name="User3",
            phone="1234567890",
        )
        other_workspace = Workspace.objects.create(owner=user3, created_by=user3)
        other_member = WorkspaceMember.objects.create(
            user=user3, workspace=other_workspace, added_by=user3
        )
        MemberPermissions.objects.create(
            workspace=other_workspace,
            member=other_member,
            is_owner=True,
            manage_workspace_members=True,
        )
        self.client.force_authenticate(user=user3)

        response = self.client.put(self.url, {"manage_workspace_roles": True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.permissions.refresh_from_db()
        self.assertFalse(self.permissions.manage_workspace_roles)
