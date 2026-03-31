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
        self.url = reverse("workspace_roles", kwargs={"workspace_id": self.workspace.id})

    def test_invalid_workspace(self):
        """Verify that a nonexistent workspace_id returns 404."""
        url = reverse("workspace_roles", kwargs={"workspace_id": 999})
        data = {"name": "test name1", "pay_rate": 15.00}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_workspace_role_valid(self):
        """Verify that a valid role creation request returns 201 and persists the role with correct attributes."""
        data = {"name": "test name1", "pay_rate": 15.00}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        role = WorkspaceRole.objects.get(workspace=self.workspace, name=data["name"])

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, data["name"])
        self.assertEqual(role.pay_rate, data["pay_rate"])

    def test_create_workspace_role_no_name_or_payrate(self):
        """Verify that omitting name and pay_rate creates a role with defaults of 'Unnamed Role' and no pay rate."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        role = WorkspaceRole.objects.get(workspace=self.workspace)

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, "Unnamed Role")
        self.assertEqual(role.pay_rate, None)

    def test_create_workspace_role_without_permissions(self):
        """Verify that a member without manage_workspace_roles permission receives 403."""
        data = {"name": "test name1", "pay_rate": 15.00}

        self.client.force_authenticate(user=self.user2)

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_workspace_role_as_non_member(self):
        """Verify that a user who is not a workspace member receives 403."""
        data = {"name": "test name1", "pay_rate": 15.00}

        self.client.force_authenticate(user=self.user3)

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetRoleTests(APITestCase):
    """Integration tests for retrieving a workspace role."""

    def setUp(self):
        """Create a workspace, owner, unprivileged member, and a role."""
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

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Test Role", pay_rate=20.00
        )

        self.client.force_authenticate(user=self.member.user)
        self.url = reverse("role", kwargs={"role_id": self.role.id})

    def test_get_role_valid(self):
        """Verify that a workspace member can retrieve a role and response contains correct attributes."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"]["id"], self.role.id)
        self.assertEqual(response.data["result"]["name"], self.role.name)

    def test_get_role_as_unprivileged_member(self):
        """Verify that a member without manage_workspace_roles permission can still retrieve a role."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"]["id"], self.role.id)
        self.assertEqual(response.data["result"]["name"], self.role.name)

    def test_get_role_invalid_role_id(self):
        """Verify that a nonexistent role_id returns 404."""
        url = reverse("role", kwargs={"role_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_role_as_non_member(self):
        """Verify that a user who is not a member of the role's workspace receives 404."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteRoleTests(APITestCase):
    """Integration tests for deleting workspace roles."""

    def setUp(self):
        """Create a workspace, owner with manage_workspace_roles permission, and three roles."""
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

    def test_invalid_workspace_id(self):
        """Verify that a nonexistent role_id returns 404."""
        url = reverse("role", kwargs={"role_id": 999})
        response = self.client.delete(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_valid(self):
        """Verify that deleting a valid role returns 200 and removes the role from the database."""
        url = reverse("role", kwargs={"role_id": self.role.id})
        response = self.client.delete(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(WorkspaceRole.objects.filter(id=self.role.id).exists())

    def test_delete_with_children(self):
        """Verify that deleting a role with assigned MemberRoles returns 200 and cascades deletion to MemberRoles."""
        member_role = MemberRole.objects.create(workspace_role=self.role, member=self.member2)

        url = reverse("role", kwargs={"role_id": self.role.id})
        response = self.client.delete(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(WorkspaceRole.objects.filter(id=self.role.id).exists())
        self.assertFalse(MemberRole.objects.filter(id=member_role.id).exists())

    def test_delete_cross_workspace_isolation(self):
        """Verify that a privileged member of another workspace cannot delete a role in this workspace."""
        other_workspace = Workspace.objects.create(owner=self.user3, created_by=self.user3)
        other_member = WorkspaceMember.objects.create(
            user=self.user3, workspace=other_workspace, added_by=self.user3
        )
        MemberPermissions.objects.create(
            workspace=other_workspace,
            member=other_member,
            is_owner=True,
            manage_workspace_roles=True,
        )
        self.client.force_authenticate(user=self.user3)

        url = reverse("role", kwargs={"role_id": self.role.id})
        response = self.client.delete(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(WorkspaceRole.objects.filter(id=self.role.id).exists())


class ModifyWorkspaceRoleTests(APITestCase):
    """Integration tests for modifying workspace role attributes."""

    def setUp(self):
        """Create a workspace, owner with manage_workspace_roles permission, and three roles."""
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

    def test_invalid_workspace_role_id(self):
        """Verify that a nonexistent role_id returns 404."""
        url = reverse("role", kwargs={"role_id": 999})
        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_modify_valid(self):
        """Verify that a valid modification request returns 200 and updates the role's name and pay rate."""
        url = reverse("role", kwargs={"role_id": self.role.id})
        data = {"name": "new name", "pay_rate": 25}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        role = WorkspaceRole.objects.get(id=self.role.id)
        self.assertEqual(role.name, data["name"])
        self.assertEqual(role.pay_rate, data["pay_rate"])

    def test_modify_without_permissions(self):
        """Verify that a member without manage_workspace_roles permission receives 403 and the role is unchanged."""
        self.client.force_authenticate(user=self.member2.user)
        url = reverse("role", kwargs={"role_id": self.role.id})
        data = {"name": "new name", "pay_rate": 25}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role = WorkspaceRole.objects.get(id=self.role.id)
        self.assertEqual(role.name, self.role.name)
        self.assertEqual(role.pay_rate, self.role.pay_rate)

    def test_modify_cross_workspace_isolation(self):
        """Verify that a privileged member of another workspace cannot modify a role in this workspace."""
        other_workspace = Workspace.objects.create(owner=self.user3, created_by=self.user3)
        other_member = WorkspaceMember.objects.create(
            user=self.user3, workspace=other_workspace, added_by=self.user3
        )
        MemberPermissions.objects.create(
            workspace=other_workspace,
            member=other_member,
            is_owner=True,
            manage_workspace_roles=True,
        )
        self.client.force_authenticate(user=self.user3)

        url = reverse("role", kwargs={"role_id": self.role.id})
        response = self.client.put(url, {"name": "hacked", "pay_rate": 0}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        role = WorkspaceRole.objects.get(id=self.role.id)
        self.assertEqual(role.name, self.role.name)
        self.assertEqual(role.pay_rate, self.role.pay_rate)
