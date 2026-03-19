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
        self.url = reverse("workspace")
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
        """Verify that a 400 is returned when the user has no memberships."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_as_owner(self):
        """Verify that a workspace owner can retrieve workspace details."""
        self.client.force_authenticate(user=self.user)
        url = reverse("workspace_parameters", args=[self.workspace1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(result["id"], self.workspace1.id)
        self.assertEqual(result["name"], self.workspace1.name)
        self.assertEqual(result["owner"]["first_name"], self.user.first_name)
        self.assertEqual(result["owner"]["last_name"], self.user.last_name)

    def test_as_employee(self):
        """Verify that a non-owner member can retrieve workspace details."""
        self.client.force_authenticate(user=self.user2)
        url = reverse("workspace_parameters", args=[self.workspace1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(result["id"], self.workspace1.id)
        self.assertEqual(result["name"], self.workspace1.name)
        self.assertEqual(result["owner"]["first_name"], self.user.first_name)
        self.assertEqual(result["owner"]["last_name"], self.user.last_name)

    def test_no_workspace(self):
        """Verify that a 400 is returned when workspace_id is omitted from the request."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        """Verify that a 404 is returned when the requested workspace does not exist."""
        self.client.force_authenticate(user=self.user)
        url = reverse("workspace_parameters", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetWorkspaceMembersTests(APITestCase):
    def setUp(self):        
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

        self.member_role1 = MemberRole.objects.create(
            member=self.member, workspace_role=self.role
        )
        self.member2_role1 = MemberRole.objects.create(
            member=self.member2, workspace_role=self.role
        )
        self.member2_role2 = MemberRole.objects.create(
            member=self.member2, workspace_role=self.role2
        )

    def test_invalid_workspace(self):
        self.url = reverse("workspace_members", kwargs={"workspace_id": 999})
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_as_non_member(self):
        self.client.force_authenticate(user=self.user3)

        self.url = reverse(
            "workspace_members", kwargs={"workspace_id": self.workspace.id}
        )
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid(self):
        self.url = reverse(
            "workspace_members", kwargs={"workspace_id": self.workspace.id}
        )
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(len(result), 2)

        def build_expected_member(user, roles):
            return {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "member_roles": [
                    {"id": role.id, "name": role.name}
                    for role in roles
                ],
            }

        expected_member1 = build_expected_member(self.user, [self.role])
        expected_member2 = build_expected_member(self.user2, [self.role, self.role2])

        self.assertEqual(result[0], expected_member1)
        self.assertEqual(result[1], expected_member2)
