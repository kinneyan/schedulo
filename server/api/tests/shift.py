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

class ModifyShiftTests(APITestCase):
    def setUp(self):
        self.url = reverse('modify_shift')
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
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name2")

        self.time1 = datetime.now(timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)
        self.time3 = self.time1 + timedelta(hours=4)
        self.time4 = self.time1 - timedelta(hours=2)

        self.shift = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time1,
            end_time=self.time2,
            role=self.role,
            created_by=self.member,
            open=True,
        )

        self.client.force_authenticate(user=self.member.user)

    def test_no_shift(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_shift(self):
        data = {'shift_id': 999}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_without_permissions(self):
        self.client.force_authenticate(user=self.member2.user)

        data = {'shift_id': self.shift.id, 'start_time': self.time4, 'end_time': self.time3}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ensure shift was not modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time1, end_time=self.time2)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_start_and_end(self):
        data = {'shift_id': self.shift.id, 'start_time': 100, 'end_time': 100}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time1, end_time=self.time2)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_start_and_end_order(self):
        data = {'shift_id': self.shift.id, 'start_time': self.time3, 'end_time': self.time4}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time1, end_time=self.time2)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_start(self):
        data = {'shift_id': self.shift.id, 'start_time': self.time3}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time1, end_time=self.time2)
        except Shift.DoesNotExist:
            self.assertTrue(False)
    
    def test_invalid_end(self):
        data = {'shift_id': self.shift.id, 'end_time': self.time4}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time1, end_time=self.time2)        
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_start_and_end(self):
        data = {'shift_id': self.shift.id, 'start_time': self.time4, 'end_time': self.time3}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time4, end_time=self.time3)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_start(self):
        data = {'shift_id': self.shift.id, 'start_time': self.time4}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time4, end_time=self.time2)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_end(self):
        data = {'shift_id': self.shift.id, 'end_time': self.time3}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, start_time=self.time1, end_time=self.time3)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_member(self):
        data = {'shift_id': self.shift.id, 'member_id': 999}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # ensure shift was not modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, open=True)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_member(self):
        data = {'shift_id': self.shift.id, 'member_id': self.member.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, member=self.member, open=False)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_role(self):
        data = {'shift_id': self.shift.id, 'role_id': 999}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # ensure shift was not modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, role=self.role)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_role(self):
        data = {'shift_id': self.shift.id, 'role_id': self.role2.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, role=self.role2)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_modify_multiple(self):
        data = {'shift_id': self.shift.id, 'role_id': self.role2.id, 'member_id': self.member2.id, 'start_time': self.time4, 'end_time': self.time3}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            shift = Shift.objects.get(pk=self.shift.id, role=self.role2, member=self.member2, start_time=self.time4, end_time=self.time3)
        except Shift.DoesNotExist:
            self.assertTrue(False)

class DeleteShiftTests(APITestCase):
    def setUp(self):
        self.url = reverse('delete_shift')
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
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name2")

        self.time1 = datetime.now(timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)
        self.time3 = self.time1 + timedelta(hours=4)
        self.time4 = self.time1 - timedelta(hours=2)

        self.shift1 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time1,
            end_time=self.time2,
            role=self.role,
            created_by=self.member,
            open=True,
        )

        self.shift2 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time2,
            end_time=self.time3,
            role=self.role,
            created_by=self.member,
            open=False,
            member=self.member2,
        )

        self.client.force_authenticate(user=self.member.user)
    
    def test_no_shift(self):
        data = {}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_shift(self):
        data = {'shift_id': 999}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_without_permissions(self):
        # change to send from user 2
        self.client.force_authenticate(user=self.member2.user)

        data = {'shift_id': self.shift1.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that shift was not deleted
        try:
            shift = Shift.objects.get(pk=self.shift1.id)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid(self):
        data = {'shift_id': self.shift1.id}
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that shift was deleted
        try:
            shift = Shift.objects.get(pk=self.shift1.id)
            self.assertTrue(False)
        except Shift.DoesNotExist:
            self.assertTrue(True)

        # check that other shift was not deleted
        try:
            shift = Shift.objects.get(pk=self.shift2.id)
        except Shift.DoesNotExist:
            self.assertTrue(False)