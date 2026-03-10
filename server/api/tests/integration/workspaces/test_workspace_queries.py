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


class GetWorkspaceTests(APITestCase):
    """Integration tests for the get workspace endpoint."""

    def setUp(self):
        """Create two workspaces with members and authenticate test users."""
        self.url = reverse("get_workspace")
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

        self.workspace1 = Workspace.objects.create(
            owner=self.user, created_by=self.user
        )
        self.workspace1_member1 = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace1, added_by=self.user
        )
        self.workspace1_permissions1 = MemberPermissions.objects.create(
            workspace=self.workspace1,
            member=self.workspace1_member1,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )
        self.workspace1_member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace1, added_by=self.user
        )
        self.workspace1_permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace1,
            member=self.workspace1_member2,
            is_owner=False,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.workspace2 = Workspace.objects.create(
            owner=self.user, created_by=self.user
        )
        self.workspace2_member1 = WorkspaceMember.objects.create(
            user=self.user, workspace=self.workspace2, added_by=self.user
        )
        self.workspace2_permissions1 = MemberPermissions.objects.create(
            workspace=self.workspace2,
            member=self.workspace2_member1,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

    def test_no_workspaces(self):
        """Verify that a 400 is returned when no workspace_id is provided and the user has no memberships."""
        self.client.force_authenticate(user=self.user3)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Workspace ID is required", response.data["error"]["message"])

    def test_as_owner(self):
        """Verify that a workspace owner can retrieve workspace details with membership set to owner."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {"workspace_id": self.workspace1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.workspace1.name)
        self.assertEqual(
            response.data["owner_name"],
            self.workspace1.owner.first_name + " " + self.workspace1.owner.last_name,
        )
        self.assertEqual(response.data["membership"], "owner")

    def test_as_employee(self):
        """Verify that a non-owner member can retrieve workspace details with membership set to employee."""
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(self.url, {"workspace_id": self.workspace1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.workspace1.name)
        self.assertEqual(
            response.data["owner_name"],
            self.workspace1.owner.first_name + " " + self.workspace1.owner.last_name,
        )
        self.assertEqual(response.data["membership"], "employee")

    def test_no_workspace(self):
        """Verify that a 400 is returned when workspace_id is omitted from the request."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Workspace ID is required", response.data["error"]["message"])

    def test_invalid_workspace(self):
        """Verify that a 404 is returned when the requested workspace does not exist."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {"workspace_id": 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetWorkspaceMembersTests(APITestCase):
    def setUp(self):
        self.url = reverse("get_workspace_members")
        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpassword",
            first_name="Test3",
            last_name="User3",
            phone="1234567890",
        )
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

        self.member_role1 = MemberRole.objects.create(
            member=self.member, workspace_role=self.role
        )
        self.member2_role1 = MemberRole.objects.create(
            member=self.member2, workspace_role=self.role
        )
        self.member2_role2 = MemberRole.objects.create(
            member=self.member2, workspace_role=self.role2
        )

    def test_no_workspace(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        response = self.client.post(self.url, {"workspace_id": 999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_as_non_member(self):
        self.client.force_authenticate(user=self.user3)

        response = self.client.post(
            self.url, {"workspace_id": self.workspace.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid(self):
        response = self.client.post(
            self.url, {"workspace_id": self.workspace.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["members"]
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]["member_id"], self.member.id)
        self.assertEqual(result[0]["user_id"], self.user.id)
        self.assertEqual(result[0]["first_name"], self.user.first_name)
        self.assertEqual(result[0]["last_name"], self.user.last_name)
        self.assertEqual(result[0]["email"], self.user.email)
        self.assertEqual(len(result[0]["roles"]), 1)
        self.assertEqual(result[0]["roles"][0]["role_id"], self.role.id)
        self.assertEqual(result[0]["roles"][0]["name"], self.role.name)
        self.assertEqual(result[0]["roles"][0]["pay_rate"], self.role.pay_rate)
        self.assertEqual(
            result[0]["permissions"]["is_owner"], self.permissions.is_owner
        )
        self.assertEqual(
            result[0]["permissions"]["manage_workspace_members"],
            self.permissions.manage_workspace_members,
        )
        self.assertEqual(
            result[0]["permissions"]["manage_workspace_roles"],
            self.permissions.manage_workspace_roles,
        )
        self.assertEqual(
            result[0]["permissions"]["manage_schedules"],
            self.permissions.manage_schedules,
        )
        self.assertEqual(
            result[0]["permissions"]["manage_time_off"],
            self.permissions.manage_time_off,
        )

        self.assertEqual(result[1]["member_id"], self.member2.id)
        self.assertEqual(result[1]["user_id"], self.user2.id)
        self.assertEqual(result[1]["first_name"], self.user2.first_name)
        self.assertEqual(result[1]["last_name"], self.user2.last_name)
        self.assertEqual(result[1]["email"], self.user2.email)
        self.assertEqual(len(result[1]["roles"]), 2)
        self.assertEqual(result[1]["roles"][0]["role_id"], self.role.id)
        self.assertEqual(result[1]["roles"][0]["name"], self.role.name)
        self.assertEqual(result[1]["roles"][0]["pay_rate"], self.role.pay_rate)
        self.assertEqual(result[1]["roles"][1]["role_id"], self.role2.id)
        self.assertEqual(result[1]["roles"][1]["name"], self.role2.name)
        self.assertEqual(result[1]["roles"][1]["pay_rate"], self.role2.pay_rate)
        self.assertEqual(
            result[1]["permissions"]["is_owner"], self.permissions2.is_owner
        )
        self.assertEqual(
            result[1]["permissions"]["manage_workspace_members"],
            self.permissions2.manage_workspace_members,
        )
        self.assertEqual(
            result[1]["permissions"]["manage_workspace_roles"],
            self.permissions2.manage_workspace_roles,
        )
        self.assertEqual(
            result[1]["permissions"]["manage_schedules"],
            self.permissions2.manage_schedules,
        )
        self.assertEqual(
            result[1]["permissions"]["manage_time_off"],
            self.permissions2.manage_time_off,
        )
