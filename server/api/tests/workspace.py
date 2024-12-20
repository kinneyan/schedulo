from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Workspace, WorkspaceMember, User, MemberPermissions

class AddMemberTests(APITestCase):
    def setUp(self):
        self.url = reverse("add_workspace_member")

        # add users
        self.user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        self.user = User.objects.create_user(**self.user_data)

        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

        self.other_user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "0987654321"
        }
        self.other_user = User.objects.create_user(**self.other_user_data)

        # add workspace
        self.workspace = Workspace.objects.create(created_by=self.user, owner=self.user)
        self.workspace_member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permission = MemberPermissions.objects.create(member=self.workspace_member, workspace=self.workspace, MANAGE_WORKSPACE_MEMBERS=True)

    def test_add_workspace_member_permission(self):
        data = {
            'added_user_id': self.other_user.id,
            'workspace_id': self.workspace.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_workspace_member_no_permission(self):
        self.permission.MANAGE_WORKSPACE_MEMBERS = False
        self.permission.save()
        data = {
            'added_user_id': self.other_user.id,
            'workspace_id': self.workspace.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "You do not have permission to add members to this workspace")

    def test_add_duplicate_workspace_member(self):
        # Add the user as a workspace member for the first time
        data = {
            'added_user_id': self.other_user.id,
            'workspace_id': self.workspace.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to add the same user again
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error"], "User is already member of this workspace")

class ModifyWorkspaceTests(APITestCase):
    def setUp(self):
        self.url = reverse('modify_workspace')
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
        self.user3 = User.objects.create_user(
            email='testuser3@example.com',
            password='testpassword',
            first_name='Test3',
            last_name='User3',
            phone='1234567890'
        )

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user)
        self.member = WorkspaceMember.objects.create(user=self.user, workspace=self.workspace, added_by=self.user)
        self.permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            IS_OWNER=True,
            MANAGE_WORKSPACE_MEMBERS=True,
            MANAGE_WORKSPACE_ROLES=True,
            MANAGE_SCHEDULES=True,
            MANAGE_TIME_OFF=True
        )
        self.client.force_authenticate(user=self.member.user)

    def test_missing_workspace_id(self):
        response = self.client.put(self.url, {"member_id": self.member.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["message"], "Workspace ID is required.")

    def test_member_not_found(self):
        response = self.client.put(self.url, {"workspace_id": self.workspace.id, "new_owner_id": 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["message"], "Could not find member with provided ID.")

    def test_change_owner_valid(self):
        # add user2 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(self.url, {"workspace_id": self.workspace.id, "added_user_id": self.user2.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # set user2 to owner
        self.url = reverse("modify_workspace")
        response = self.client.put(self.url, {
            "workspace_id": self.workspace.id,
            "new_owner_id": self.user2.id
        })

        self.permissions.refresh_from_db()
        perms = MemberPermissions.objects.get(member=WorkspaceMember.objects.get(user=self.user2, workspace=self.workspace), workspace=self.workspace)

        self.assertTrue(perms.IS_OWNER)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.permissions.IS_OWNER)

    def test_change_owner_to_non_workplace_member(self):
        # set user2 to owner
        self.url = reverse("modify_workspace")
        response = self.client.put(self.url, {
            "workspace_id": self.workspace.id,
            "new_owner_id": self.user2.id
        })

        self.permissions.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(self.permissions.IS_OWNER)

    def test_change_owner_to_self(self):
        # set user to owner
        self.url = reverse("modify_workspace")
        response = self.client.put(self.url, {
            "workspace_id": self.workspace.id,
            "new_owner_id": self.user.id
        })

        self.permissions.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(self.permissions.IS_OWNER)

    def test_change_owner_as_not_owner(self):
         # add user2 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(self.url, {"workspace_id": self.workspace.id, "added_user_id": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

         # add user3 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(self.url, {"workspace_id": self.workspace.id, "added_user_id": self.user3.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.url = reverse("modify_workspace")
        self.client.force_authenticate(user=self.user2) # change to send request from user 2

        # try to change user 3 to owner
        response = self.client.put(self.url, {
            "workspace_id": self.workspace.id,
            "new_owner_id": self.user3.id
        })

        perms = MemberPermissions.objects.get(member=WorkspaceMember.objects.get(user=self.user3, workspace=self.workspace), workspace=self.workspace)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.permissions.IS_OWNER)
        self.assertFalse(perms.IS_OWNER)


    def test_change_name_valid(self):
        self.url = reverse("modify_workspace")
        response = self.client.put(self.url, {
            "workspace_id": self.workspace.id,
            "name": "new name"
        })

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.workspace.name, "new name")

    def test_change_name_as_non_member(self):
        self.url = reverse("modify_workspace")
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(self.url, {
            "workspace_id": self.workspace.id,
            "name": "new name"
        })

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.workspace.name, "Unnamed Workspace")

    def test_change_name_as_not_owner(self):
         # add user2 to workspace
        self.url = reverse("add_workspace_member")
        response = self.client.post(self.url, {"workspace_id": self.workspace.id, "added_user_id": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.url = reverse("modify_workspace")
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(self.url, {
            "workspace_id": self.workspace.id,
            "name": "new name"
        })

        self.workspace.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.workspace.name, "Unnamed Workspace")


