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


class GetRolesTests(APITestCase):
    """Integration tests for retrieving workspace roles."""

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
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_single(self):
        """Verify that retrieving roles for a workspace with one role returns that role correctly."""
        data = {"name": "test name1", "pay_rate": 15.00}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        output = response.data["result"]
        role = WorkspaceRole.objects.get(id=output[0]["id"])

        self.assertEqual(role.name, data["name"])

    def test_multiple(self):
        """Verify that retrieving roles for a workspace with multiple roles returns all of them."""
        data = []
        data.append({"name": "test name1", "pay_rate": 15.00})
        data.append({"name": "test name2", "pay_rate": 10.00})
        data.append({"name": "test name3", "pay_rate": 18.00})

        for i in range(3):
            response = self.client.post(self.url, data[i], format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        output = response.data["result"]

        self.assertEqual(len(output), len(data))

        for i in range(len(data)):
            role = WorkspaceRole.objects.get(id=output[i]["id"])
            self.assertEqual(data[i]["name"], output[i]["name"])
            self.assertEqual(data[i]["name"], role.name)

    def test_multiple_workspaces(self):
        """Verify that fetching roles for one workspace does not include roles from another workspace."""
        self.workspace2 = Workspace.objects.create(owner=self.user, created_by=self.user)

        self.member5 = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace2, added_by=self.user
        )
        self.permissions5 = MemberPermissions.objects.create(
            workspace=self.workspace2,
            member=self.member5,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        workspace2_url = reverse("workspace_roles", kwargs={"workspace_id": self.workspace2.id})
        response = self.client.post(
            workspace2_url,
            {"name": "test name4", "pay_rate": 5.00},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = []
        data.append({"name": "test name1", "pay_rate": 15.00})
        data.append({"name": "test name2", "pay_rate": 10.00})
        data.append({"name": "test name3", "pay_rate": 18.00})

        for i in range(3):
            response = self.client.post(self.url, data[i], format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        output = response.data["result"]

        self.assertEqual(len(output), len(data))

        for i in range(len(data)):
            role = WorkspaceRole.objects.get(id=output[i]["id"])
            self.assertEqual(data[i]["name"], output[i]["name"])
            self.assertEqual(data[i]["name"], role.name)


class GetMemberRoleTests(APITestCase):
    """Integration tests for retrieving roles assigned to a workspace member."""

    def setUp(self):
        """Create a workspace, owner, member, and three workspace roles."""
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

    def test_invalid_member_id(self):
        """Verify that a nonexistent member_id returns 404."""
        url = reverse("member_roles", kwargs={"member_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_roles(self):
        """Verify that fetching roles for a member with no assignments returns an empty list."""
        url = reverse("member_roles", kwargs={"member_id": self.member2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["result"]), 0)

    def test_single(self):
        """Verify that fetching roles for a member with one assignment returns that role."""
        MemberRole.objects.create(workspace_role=self.role, member=self.member2)

        url = reverse("member_roles", kwargs={"member_id": self.member2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["result"]), 1)

        role = WorkspaceRole.objects.get(id=response.data["result"][0]["id"])
        self.assertEqual(self.role.id, role.id)

    def test_multiple(self):
        """Verify that fetching roles for a member with multiple assignments returns all of them in order."""
        MemberRole.objects.create(workspace_role=self.role, member=self.member2)
        MemberRole.objects.create(workspace_role=self.role2, member=self.member2)
        MemberRole.objects.create(workspace_role=self.role3, member=self.member2)

        url = reverse("member_roles", kwargs={"member_id": self.member2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["result"]), 3)

        role = WorkspaceRole.objects.get(id=response.data["result"][0]["id"])
        role2 = WorkspaceRole.objects.get(id=response.data["result"][1]["id"])
        role3 = WorkspaceRole.objects.get(id=response.data["result"][2]["id"])
        self.assertEqual(self.role.id, role.id)
        self.assertEqual(self.role2.id, role2.id)
        self.assertEqual(self.role3.id, role3.id)
