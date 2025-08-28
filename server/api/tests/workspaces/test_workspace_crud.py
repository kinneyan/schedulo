from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ...models import Workspace, WorkspaceMember, User, MemberPermissions


class ModifyWorkspaceTests(APITestCase):
    def setUp(self):
        self.url = reverse("modify_workspace")
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
        self.client.force_authenticate(user=self.member.user)

    def test_missing_workspace_id(self):
        response = self.client.put(self.url, {"member_id": self.member.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["message"], "Workspace ID is required.")

    def test_member_not_found(self):
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "new_owner_id": 999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"]["message"], "Could not find member with provided ID."
        )

    def test_change_owner_valid(self):
        # add user2 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(
            self.url,
            {"workspace_id": self.workspace.id, "added_user_id": self.user2.id},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # set user2 to owner
        self.url = reverse("modify_workspace")
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "new_owner_id": self.user2.id}
        )

        self.permissions.refresh_from_db()
        perms = MemberPermissions.objects.get(
            member=WorkspaceMember.objects.get(
                user=self.user2, workspace=self.workspace
            ),
            workspace=self.workspace,
        )

        self.assertTrue(perms.IS_OWNER)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.permissions.IS_OWNER)

    def test_change_owner_to_non_workplace_member(self):
        # set user2 to owner
        self.url = reverse("modify_workspace")
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "new_owner_id": self.user2.id}
        )

        self.permissions.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.permissions.IS_OWNER)

    def test_change_owner_to_self(self):
        # set user to owner
        self.url = reverse("modify_workspace")
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "new_owner_id": self.user.id}
        )

        self.permissions.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(self.permissions.IS_OWNER)

    def test_change_owner_as_not_owner(self):
        # add user2 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(
            self.url,
            {"workspace_id": self.workspace.id, "added_user_id": self.user2.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # add user3 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(
            self.url,
            {"workspace_id": self.workspace.id, "added_user_id": self.user3.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.url = reverse("modify_workspace")
        self.client.force_authenticate(
            user=self.user2
        )  # change to send request from user 2

        # try to change user 3 to owner
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "new_owner_id": self.user3.id}
        )

        perms = MemberPermissions.objects.get(
            member=WorkspaceMember.objects.get(
                user=self.user3, workspace=self.workspace
            ),
            workspace=self.workspace,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.permissions.IS_OWNER)
        self.assertFalse(perms.IS_OWNER)

    def test_change_name_valid(self):
        self.url = reverse("modify_workspace")
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "name": "new name"}
        )

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.workspace.name, "new name")

    def test_change_name_as_non_member(self):
        self.url = reverse("modify_workspace")
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "name": "new name"}
        )

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.workspace.name, "Unnamed Workspace")

    def test_change_name_as_not_owner(self):
        # add user2 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(
            self.url,
            {"workspace_id": self.workspace.id, "added_user_id": self.user2.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.url = reverse("modify_workspace")
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(
            self.url, {"workspace_id": self.workspace.id, "name": "new name"}
        )

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.workspace.name, "Unnamed Workspace")


class DeleteWorkspaceTests(APITestCase):
    def setUp(self):
        self.url = reverse("delete_workspace")
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
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
        )
        self.workspace1_member2 = WorkspaceMember.objects.create(
            user=self.user2, workspace=self.workspace1, added_by=self.user
        )
        self.workspace1_permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace1,
            member=self.workspace1_member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
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
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_no_workspace_id(self):
        response = self.client.delete(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_id(self):
        response = self.client.delete(self.url, {"workspace_id": 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.url, {"workspace_id": self.workspace1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ensure workspace was not deleted
        try:
            workspace = Workspace.objects.get(pk=self.workspace1.id)
        except Workspace.DoesNotExist:
            self.assertTrue(False)

    def test_not_member(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.delete(self.url, {"workspace_id": self.workspace1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ensure workspace was not deleted
        try:
            workspace = Workspace.objects.get(pk=self.workspace1.id)
        except Workspace.DoesNotExist:
            self.assertTrue(False)

    def test_valid(self):
        response = self.client.delete(self.url, {"workspace_id": self.workspace1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure workspace was deleted
        try:
            workspace = Workspace.objects.get(pk=self.workspace1.id)
            self.assertTrue(False)
        except Workspace.DoesNotExist:
            self.assertTrue(True)