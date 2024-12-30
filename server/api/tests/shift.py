from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta, timezone
from ..models import Workspace, WorkspaceMember, User, MemberPermissions, WorkspaceRole, MemberRole, Shift

class CreateShiftTests(APITestCase):
    def setUp(self):
        self.url = reverse('create_shift')
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

        self.member2 = WorkspaceMember.objects.create(user=self.user2, workspace=self.workspace, added_by=self.user)
        self.permissions2 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member2,
            IS_OWNER=False,
            MANAGE_WORKSPACE_MEMBERS=False,
            MANAGE_WORKSPACE_ROLES=False,
            MANAGE_SCHEDULES=False,
            MANAGE_TIME_OFF=False
        )

        self.role = WorkspaceRole.objects.create(workspace=self.workspace, name="test name")

        self.time1 = datetime.now(timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)

        self.client.force_authenticate(user=self.member.user)

    def test_no_workspace(self):
        data = {'role_id': self.role.id, 'start_time': self.time1, 'end_time': self.time2}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        data = {'workspace_id': 999, 'role_id': self.role.id, 'start_time': self.time1, 'end_time': self.time2}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_role(self):
        data = {'workspace_id': self.workspace.id, 'start_time': self.time1, 'end_time': self.time2}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        data = {'workspace_id': self.workspace.id, 'role_id': 999, 'start_time': self.time1, 'end_time': self.time2}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_time(self):
        data = {'workspace_id': self.workspace.id, 'role_id': self.role.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_time_before_start(self):
        data = {'workspace_id': self.workspace.id, 'role_id': self.role.id, 'start_time': self.time2, 'end_time': self.time1}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_permissions(self):
        self.client.force_authenticate(user=self.member2.user)
        data = {'workspace_id': self.workspace.id, 'role_id': self.role.id, 'start_time': self.time2, 'end_time': self.time1}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that shift was not created in db
        try:
            shift = Shift.objects.get(workspace=self.workspace, role=self.role, start_time=self.time1, end_time=self.time2, open=True)
            self.assertTrue(False)
        except Shift.DoesNotExist:
            self.assertTrue(True)

    def test_valid(self):
        data = {'workspace_id': self.workspace.id, 'role_id': self.role.id, 'start_time': self.time1, 'end_time': self.time2}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that shift was created in db
        try:
            shift = Shift.objects.get(workspace=self.workspace, role=self.role, start_time=self.time1, end_time=self.time2, open=True)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_with_member(self):
        data = {'workspace_id': self.workspace.id, 'role_id': self.role.id, 'start_time': self.time1, 'end_time': self.time2, 'member_id': self.member2.id}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that shift was created in db
        try:
            shift = Shift.objects.get(workspace=self.workspace, role=self.role, start_time=self.time1, end_time=self.time2, open=False, member=self.member2)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_with_invalid_member(self):
        data = {'workspace_id': self.workspace.id, 'role_id': self.role.id, 'start_time': self.time1, 'end_time': self.time2, 'member_id': 999}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # check that shift not was created in db
        try:
            shift = Shift.objects.get(workspace=self.workspace, role=self.role, start_time=self.time1, end_time=self.time2)
            self.assertTrue(False)
        except Shift.DoesNotExist:
            self.assertTrue(True)
