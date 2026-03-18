from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ....models import Workspace, WorkspaceMember, User, MemberPermissions


class ModifyWorkspaceTests(APITestCase):
    """Integration tests for the modify workspace endpoint."""

    def setUp(self):
        """Create a workspace with an authenticated owner and two additional users."""
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

        self.client.force_authenticate(user=self.member.user)

    def test_missing_workspace_id(self):
        """Verify that a 404 is returned when workspace_id is absent from the request."""
        # response = self.client.put(self.url, {"new_owner_id": self.member.id})
        response = self.client.put("workspace/", {"new_owner_id": self.member.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_not_found(self):
        """Verify that a 404 is returned when the target new owner does not exist."""
        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        response = self.client.put(self.url, {"new_owner_id": 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"]["message"], "Could not find member with provided ID."
        )

    def test_change_owner_valid(self):
        """Verify that an owner can transfer ownership to an existing workspace member."""
        # set user2 to owner
        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        response = self.client.put(self.url, {"new_owner_id": self.user2.id})

        self.permissions.refresh_from_db()
        perms = MemberPermissions.objects.get(
            member=WorkspaceMember.objects.get(
                user=self.user2, workspace=self.workspace
            ),
            workspace=self.workspace,
        )

        self.assertTrue(perms.is_owner)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.permissions.is_owner)

    def test_change_owner_to_non_workplace_member(self):
        """Verify that ownership cannot be transferred to a user who is not a workspace member."""
        # set user3 to owner
        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        response = self.client.put(self.url, {"new_owner_id": self.user4.id})

        self.permissions.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.permissions.is_owner)

    def test_change_owner_to_self(self):
        """Verify that an owner cannot transfer ownership to themselves."""
        # set user to owner
        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        response = self.client.put(self.url, {"new_owner_id": self.user.id})

        self.permissions.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(self.permissions.is_owner)

    def test_change_owner_as_not_owner(self):
        """Verify that a non-owner member cannot transfer workspace ownership."""

        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        self.client.force_authenticate(
            user=self.user2
        )  # change to send request from user 2

        # try to change user 3 to owner
        response = self.client.put(self.url, {"new_owner_id": self.user3.id})

        perms = MemberPermissions.objects.get(
            member=WorkspaceMember.objects.get(
                user=self.user3, workspace=self.workspace
            ),
            workspace=self.workspace,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.permissions.is_owner)
        self.assertFalse(perms.is_owner)

    def test_change_name_valid(self):
        """Verify that a workspace owner can rename the workspace."""
        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        response = self.client.put(self.url, {"name": "new name"})

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.workspace.name, "new name")

    def test_change_name_as_non_member(self):
        """Verify that a user who is not a workspace member cannot rename the workspace."""
        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        self.client.force_authenticate(user=self.user4)
        response = self.client.put(self.url, {"name": "new name"})

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.workspace.name, "Unnamed Workspace")

    def test_change_name_as_not_owner(self):
        """Verify that a non-owner member cannot rename the workspace."""

        self.url = reverse("workspace_parameters", args=[self.workspace.id])
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(self.url, {"name": "new name"})

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.workspace.name, "Unnamed Workspace")


class DeleteWorkspaceTests(APITestCase):
    """Integration tests for the delete workspace endpoint."""

    def setUp(self):
        """Create two workspaces with members and authenticate as the owner."""
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
        self.client.force_authenticate(user=self.user)

    def test_no_workspace_id(self):
        """Verify that a 400 is returned when workspace_id is absent from the request."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_id(self):
        """Verify that a 404 is returned when the requested workspace does not exist."""
        self.url = reverse("workspace_parameters", args=[999])
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_owner(self):
        """Verify that a non-owner member cannot delete the workspace."""
        self.client.force_authenticate(user=self.user2)
        self.url = reverse("workspace_parameters", args=[self.workspace1.id])
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(Workspace.objects.filter(pk=self.workspace1.id).exists())

    def test_not_member(self):
        """Verify that a user who is not a workspace member cannot delete the workspace."""
        self.client.force_authenticate(user=self.user3)
        self.url = reverse("workspace_parameters", args=[self.workspace1.id])
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(Workspace.objects.filter(pk=self.workspace1.id).exists())

    def test_valid(self):
        """Verify that a workspace owner can successfully delete the workspace."""
        self.url = reverse("workspace_parameters", args=[self.workspace1.id])
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(Workspace.objects.filter(pk=self.workspace1.id).exists())
