from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ....models import User, Workspace, WorkspaceMember, WorkspaceRole, MemberPermissions


class GetUserTests(APITestCase):
    def setUp(self):
        self.url = reverse("get_user")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            phone="1234567890",
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

        self.workspace = Workspace.objects.create(owner=self.user, created_by=self.user, name="workspace name")
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

        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

    def test_get_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["phone"], self.user.phone)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)


        workspaces = response.data['workspaces']
        self.assertEqual(len(workspaces), 1)
        self.assertEqual(workspaces[0]['name'], self.workspace.name)

    def test_get_user_no_workspaces(self):
        self.client.force_authenticate(user=self.user2) # send request as user2
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user2.email)
        self.assertEqual(response.data['phone'], self.user2.phone)
        self.assertEqual(response.data['first_name'], self.user2.first_name)
        self.assertEqual(response.data['last_name'], self.user2.last_name)

        workspaces = response.data['workspaces']
        self.assertEqual(len(workspaces), 0)