from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import MemberPermissions, WorkspaceMember, Workspace, User


class UpdatePermissionsTests(APITestCase):
    def setUp(self):
        self.url = reverse('update_permissions')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpassword',
            first_name='Test2',
            last_name='User2',
            phone='1234567890'
        )
        self.workspace = Workspace.objects.create(owner_id=self.user, created_by_id=self.user)
        self.member = WorkspaceMember.objects.create(user_id=self.user2, workspace_id=self.workspace, added_by_id=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace_id=self.workspace,
            member_id=self.member,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )
        self.client.force_authenticate(user=self.member.user_id)

    def test_missing_workspace_id(self):
        response = self.client.put(self.url, {"member_id": self.member.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["message"], "Workspace ID is required.")

    def test_missing_member_id(self):
        response = self.client.put(self.url, {"workspace_id": self.workspace.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["message"], "Member ID is required.")

    def test_member_not_found(self):
        response = self.client.put(self.url, {"workspace_id": self.workspace.id, "member_id": 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["message"], "Could not find member with provided ID.")

    def test_create_new_permissions(self):
        response = self.client.put(self.url, {"workspace_id": self.workspace.id, "member_id": self.member.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(MemberPermissions.objects.filter(workspace_id=self.workspace.id, member_id=self.member).exists())

    def test_cannot_update_owner_permissions(self):
        self.permissions.IS_OWNER = True
        self.permissions.save()
        response = self.client.put(self.url, {"workspace_id": self.workspace.id, "member_id": self.member.id, "manage_workspace_members": True})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error"]["message"], "Cannot update permissions for workspace owner.")

    def test_successfully_update_permissions(self):
        data = {
            "workspace_id": self.workspace.id,
            "member_id": self.member.id,
            "manage_workspace_members": True,
            "manage_workspace_roles": True,
            "manage_schedules": True,
            "manage_time_off": True
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.permissions.refresh_from_db()
        self.assertTrue(self.permissions.MANAGE_WORKSPACE_MEMBERS)
        self.assertTrue(self.permissions.MANAGE_WORKSPACE_ROLES)
        self.assertTrue(self.permissions.MANAGE_SCHEDULES)
        self.assertTrue(self.permissions.MANAGE_TIME_OFF)
