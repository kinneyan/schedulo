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


class CreateRoleTests(APITestCase):
    """Integration tests for creating workspace roles."""

    def setUp(self):
        """Create a workspace, owner with manage_workspace_roles permission, and an unprivileged member."""
        self.url = reverse("create_workspace_role")
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
        self.client.force_authenticate(user=self.member.user)

    def test_no_workspace(self):
        """Verify that omitting workspace_id returns 400."""
        data = {"name": "test name1", "pay_rate": 15.00}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        """Verify that a nonexistent workspace_id returns 404."""
        data = {"workspace_id": 999, "name": "test name1", "pay_rate": 15.00}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_workspace_role_valid(self):
        """Verify that a valid role creation request returns 201 and persists the role with correct attributes."""
        data = {
            "workspace_id": self.workspace.id,
            "name": "test name1",
            "pay_rate": 15.00,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        role = WorkspaceRole.objects.get(workspace=self.workspace, name=data["name"])

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, data["name"])
        self.assertEqual(role.pay_rate, data["pay_rate"])

    def test_create_workspace_role_no_name_or_payrate(self):
        """Verify that omitting name and pay_rate creates a role with defaults of 'Unnamed Role' and no pay rate."""
        data = {"workspace_id": self.workspace.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        role = WorkspaceRole.objects.get(workspace=self.workspace)

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, "Unnamed Role")
        self.assertEqual(role.pay_rate, None)

    def test_create_workspace_role_without_permissions(self):
        """Verify that a member without manage_workspace_roles permission receives 403."""
        data = {
            "workspace_id": self.workspace.id,
            "name": "test name1",
            "pay_rate": 15.00,
        }

        self.client.force_authenticate(
            user=self.user2
        )  # change to send request from user 2

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_workspace_role_as_non_member(self):
        """Verify that a user who is not a workspace member receives 403."""
        data = {
            "workspace_id": self.workspace.id,
            "name": "test name1",
            "pay_rate": 15.00,
        }

        self.client.force_authenticate(
            user=self.user3
        )  # change to send request from user 2

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteRoleTests(APITestCase):
    """Integration tests for deleting workspace roles."""

    def setUp(self):
        """Create a workspace, owner with manage_workspace_roles permission, and three roles."""
        self.url = reverse("delete_workspace_role")
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
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role", pay_rate=10
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role2", pay_rate=10
        )
        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role3", pay_rate=10
        )

    def test_no_workspace_role_id(self):
        """Verify that omitting workspace_role_id returns 400."""
        data = {}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_id(self):
        """Verify that a nonexistent workspace_role_id returns 404."""
        data = {"workspace_role_id": 999}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_valid(self):
        """Verify that deleting a valid role returns 200 and removes the role from the database."""
        data = {"workspace_role_id": self.role.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that role was deleted
        try:
            WorkspaceRole.objects.get(id=self.role.id)
            self.assertTrue(False)
        except WorkspaceRole.DoesNotExist:
            self.assertTrue(True)

    def test_delete_with_children(self):
        """Verify that deleting a role with assigned MemberRoles returns 200 and cascades deletion to MemberRoles."""
        member_role = MemberRole.objects.create(
            workspace_role=self.role, member=self.member2
        )  # create child member role

        data = {"workspace_role_id": self.role.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that role was deleted
        try:
            WorkspaceRole.objects.get(id=self.role.id)
            self.assertTrue(False)
        except WorkspaceRole.DoesNotExist:
            self.assertTrue(True)

        # check that member role was deleted
        try:
            MemberRole.objects.get(id=member_role.id)
            self.assertTrue(False)
        except MemberRole.DoesNotExist:
            self.assertTrue(True)


class ModifyWorkspaceRoleTests(APITestCase):
    """Integration tests for modifying workspace role attributes."""

    def setUp(self):
        """Create a workspace, owner with manage_workspace_roles permission, and three roles."""
        self.url = reverse("modify_workspace_role")
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
        self.client.force_authenticate(user=self.member.user)

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role", pay_rate=10
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role2", pay_rate=10
        )
        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test role3", pay_rate=10
        )

    def test_no_workspace_role_id(self):
        """Verify that omitting workspace_role_id returns 400."""
        data = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_role_id(self):
        """Verify that a nonexistent workspace_role_id returns 404."""
        data = {"workspace_role_id": 999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_modify_valid(self):
        """Verify that a valid modification request returns 200 and updates the role's name and pay rate."""
        data = {"workspace_role_id": self.role.id, "name": "new name", "pay_rate": 25}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that role was modified
        role = WorkspaceRole.objects.get(id=self.role.id)
        self.assertEqual(role.name, data["name"])
        self.assertEqual(role.pay_rate, data["pay_rate"])

    def test_modify_without_permissions(self):
        """Verify that a member without manage_workspace_roles permission receives 403 and the role is unchanged."""
        self.client.force_authenticate(user=self.member2.user)
        data = {"workspace_role_id": self.role.id, "name": "new name", "pay_rate": 25}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that role did not change
        role = WorkspaceRole.objects.get(id=self.role.id)
        self.assertEqual(role.name, self.role.name)
        self.assertEqual(role.pay_rate, self.role.pay_rate)
