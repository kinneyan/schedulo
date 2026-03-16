from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ....models import Workspace, WorkspaceMember, User, MemberPermissions


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
        """Verify that a 400 is returned when no workspace_id is provided and the user has no memberships."""
        self.client.force_authenticate(user=self.user3)

        self.url = reverse("workspace")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Workspace ID is required", response.data["error"]["message"])

    def test_as_owner(self):
        """Verify that a workspace owner can retrieve workspace details with membership set to owner."""
        self.client.force_authenticate(user=self.user)

        self.url = reverse("workspace_parameters", args=[self.workspace1.id])
        response = self.client.get(self.url)
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

        self.url = reverse("workspace_parameters", args=[self.workspace1.id])
        response = self.client.get(self.url)
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

        self.url = reverse("workspace")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Workspace ID is required", response.data["error"]["message"])

    def test_invalid_workspace(self):
        """Verify that a 404 is returned when the requested workspace does not exist."""
        self.client.force_authenticate(user=self.user)

        self.url = reverse("workspace_parameters", args=[999])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
