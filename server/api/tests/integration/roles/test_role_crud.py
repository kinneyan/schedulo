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
    def setUp(self):
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
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False,
        )
        self.client.force_authenticate(user=self.member.user)

    def test_no_workspace(self):
        data = {"name": "test name1", "pay_rate": 15.00}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        data = {"workspace_id": 999, "name": "test name1", "pay_rate": 15.00}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_workspace_role_valid(self):
        data = {
            "workspace_id": self.workspace.id,
            "name": "test name1",
            "pay_rate": 15.00,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        role = WorkspaceRole.objects.get(workspace=self.workspace, name=data["name"])

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, data["name"])
        self.assertEqual(role.pay_rate, data["pay_rate"])

    def test_create_workspace_role_no_name_or_payrate(self):
        data = {"workspace_id": self.workspace.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        role = WorkspaceRole.objects.get(workspace=self.workspace)

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, "Unnamed Role")
        self.assertEqual(role.pay_rate, None)

    def test_create_workspace_role_without_permissions(self):
        data = {
            "workspace_id": self.workspace.id,
            "name": "test name1",
            "pay_rate": 15.00,
        }

        self.client.force_authenticate(
            user=self.user2
        )  # change to send request from user 2

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_workspace_role_as_non_member(self):
        data = {
            "workspace_id": self.workspace.id,
            "name": "test name1",
            "pay_rate": 15.00,
        }

        self.client.force_authenticate(
            user=self.user3
        )  # change to send request from user 2

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeleteRoleTests(APITestCase):
    def setUp(self):
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
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False,
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
        data = {}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_id(self):
        data = {"workspace_role_id": 999}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_valid(self):
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
    def setUp(self):
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
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
        )

        self.member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace, added_by=self.user
        )
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False,
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
        data = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_role_id(self):
        data = {"workspace_role_id": 999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_modify_valid(self):
        data = {"workspace_role_id": self.role.id, "name": "new name", "pay_rate": 25}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that role was modified
        role = WorkspaceRole.objects.get(id=self.role.id)
        self.assertEqual(role.name, data["name"])
        self.assertEqual(role.pay_rate, data["pay_rate"])

    def test_modify_without_permissions(self):
        self.client.force_authenticate(user=self.member2.user)
        data = {"workspace_role_id": self.role.id, "name": "new name", "pay_rate": 25}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that role did not change
        role = WorkspaceRole.objects.get(id=self.role.id)
        self.assertEqual(role.name, self.role.name)
        self.assertEqual(role.pay_rate, self.role.pay_rate)
