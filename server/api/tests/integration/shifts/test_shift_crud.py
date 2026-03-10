from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta, timezone
from ....models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
    Shift,
)


class CreateShiftTests(APITestCase):
    """Integration tests for the shift creation endpoint."""

    def setUp(self):
        """Create users, workspace, members with permissions, and a role."""
        self.url = reverse("create_shift")
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

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name"
        )

        self.time1 = datetime.now(timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)

        self.client.force_authenticate(user=self.member.user)

    def test_no_workspace(self):
        """Verify that omitting workspace_id returns a 400 error."""
        data = {
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace(self):
        """Verify that a non-existent workspace_id returns a 404 error."""
        data = {
            "workspace_id": 999,
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_role(self):
        """Verify that omitting role_id returns a 400 error."""
        data = {
            "workspace_id": self.workspace.id,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        """Verify that a non-existent role_id returns a 404 error."""
        data = {
            "workspace_id": self.workspace.id,
            "role_id": 999,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_time(self):
        """Verify that omitting start_time and end_time returns a 400 error."""
        data = {"workspace_id": self.workspace.id, "role_id": self.role.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_time_before_start(self):
        """Verify that an end_time earlier than start_time returns a 400 error."""
        data = {
            "workspace_id": self.workspace.id,
            "role_id": self.role.id,
            "start_time": self.time2,
            "end_time": self.time1,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_permissions(self):
        """Verify that a member without manage_schedules permission cannot create a shift."""
        self.client.force_authenticate(user=self.member2.user)
        data = {
            "workspace_id": self.workspace.id,
            "role_id": self.role.id,
            "start_time": self.time2,
            "end_time": self.time1,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that shift was not created in db
        try:
            Shift.objects.get(
                workspace=self.workspace,
                role=self.role,
                start_time=self.time1,
                end_time=self.time2,
                open=True,
            )
            self.assertTrue(False)
        except Shift.DoesNotExist:
            self.assertTrue(True)

    def test_valid(self):
        """Verify that a valid payload creates a shift and returns 201."""
        data = {
            "workspace_id": self.workspace.id,
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that shift was created in db
        try:
            Shift.objects.get(
                workspace=self.workspace,
                role=self.role,
                start_time=self.time1,
                end_time=self.time2,
                open=True,
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_with_member(self):
        """Verify that providing a member_id creates an assigned (non-open) shift."""
        data = {
            "workspace_id": self.workspace.id,
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
            "member_id": self.member2.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that shift was created in db
        try:
            Shift.objects.get(
                workspace=self.workspace,
                role=self.role,
                start_time=self.time1,
                end_time=self.time2,
                open=False,
                member=self.member2,
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_with_invalid_member(self):
        """Verify that a non-existent member_id returns a 404 and no shift is created."""
        data = {
            "workspace_id": self.workspace.id,
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
            "member_id": 999,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # check that shift not was created in db
        try:
            Shift.objects.get(
                workspace=self.workspace,
                role=self.role,
                start_time=self.time1,
                end_time=self.time2,
            )
            self.assertTrue(False)
        except Shift.DoesNotExist:
            self.assertTrue(True)


class ModifyShiftTests(APITestCase):
    """Integration tests for the shift modification endpoint."""

    def setUp(self):
        """Create users, workspace, members with permissions, roles, and an existing shift."""
        self.url = reverse("modify_shift")
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

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name"
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name2"
        )

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
        """Verify that omitting shift_id returns a 400 error."""
        data = {}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_shift(self):
        """Verify that a non-existent shift_id returns a 404 error."""
        data = {"shift_id": 999}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_without_permissions(self):
        """Verify that a member without manage_schedules permission cannot modify a shift."""
        self.client.force_authenticate(user=self.member2.user)

        data = {
            "shift_id": self.shift.id,
            "start_time": self.time4,
            "end_time": self.time3,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ensure shift was not modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_start_and_end(self):
        """Verify that non-datetime start_time and end_time values return a 400 error."""
        data = {"shift_id": self.shift.id, "start_time": 100, "end_time": 100}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_start_and_end_order(self):
        """Verify that a start_time after end_time returns a 400 error."""
        data = {
            "shift_id": self.shift.id,
            "start_time": self.time3,
            "end_time": self.time4,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_start(self):
        """Verify that a new start_time after the existing end_time returns a 400 error."""
        data = {"shift_id": self.shift.id, "start_time": self.time3}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_end(self):
        """Verify that a new end_time before the existing start_time returns a 400 error."""
        data = {"shift_id": self.shift.id, "end_time": self.time4}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # ensure shift was not modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_start_and_end(self):
        """Verify that updating both start_time and end_time succeeds and persists the changes."""
        data = {
            "shift_id": self.shift.id,
            "start_time": self.time4,
            "end_time": self.time3,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time4, end_time=self.time3
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_start(self):
        """Verify that updating only start_time succeeds and persists the change."""
        data = {"shift_id": self.shift.id, "start_time": self.time4}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time4, end_time=self.time2
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_end(self):
        """Verify that updating only end_time succeeds and persists the change."""
        data = {"shift_id": self.shift.id, "end_time": self.time3}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            Shift.objects.get(
                pk=self.shift.id, start_time=self.time1, end_time=self.time3
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_member(self):
        """Verify that a non-existent member_id returns a 404 and the shift is unchanged."""
        data = {"shift_id": self.shift.id, "member_id": 999}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # ensure shift was not modified
        try:
            Shift.objects.get(pk=self.shift.id, open=True)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_member(self):
        """Verify that assigning a valid member marks the shift as non-open."""
        data = {"shift_id": self.shift.id, "member_id": self.member.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            Shift.objects.get(pk=self.shift.id, member=self.member, open=False)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_invalid_role(self):
        """Verify that a non-existent role_id returns a 404 and the shift role is unchanged."""
        data = {"shift_id": self.shift.id, "role_id": 999}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # ensure shift was not modified
        try:
            Shift.objects.get(pk=self.shift.id, role=self.role)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid_role(self):
        """Verify that updating to a valid role_id succeeds and persists the change."""
        data = {"shift_id": self.shift.id, "role_id": self.role2.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            Shift.objects.get(pk=self.shift.id, role=self.role2)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_modify_multiple(self):
        """Verify that updating role, member, and times together all persist correctly."""
        data = {
            "shift_id": self.shift.id,
            "role_id": self.role2.id,
            "member_id": self.member2.id,
            "start_time": self.time4,
            "end_time": self.time3,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure shift was modified
        try:
            Shift.objects.get(
                pk=self.shift.id,
                role=self.role2,
                member=self.member2,
                start_time=self.time4,
                end_time=self.time3,
            )
        except Shift.DoesNotExist:
            self.assertTrue(False)


class DeleteShiftTests(APITestCase):
    """Integration tests for the shift deletion endpoint."""

    def setUp(self):
        """Create users, workspace, members with permissions, roles, and two existing shifts."""
        self.url = reverse("delete_shift")
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

        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name"
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name2"
        )

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
        """Verify that omitting shift_id returns a 400 error."""
        data = {}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_shift(self):
        """Verify that a non-existent shift_id returns a 404 error."""
        data = {"shift_id": 999}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_without_permissions(self):
        """Verify that a member without manage_schedules permission cannot delete a shift."""
        # change to send from user 2
        self.client.force_authenticate(user=self.member2.user)

        data = {"shift_id": self.shift1.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that shift was not deleted
        try:
            Shift.objects.get(pk=self.shift1.id)
        except Shift.DoesNotExist:
            self.assertTrue(False)

    def test_valid(self):
        """Verify that a valid delete request removes the target shift and leaves others intact."""
        data = {"shift_id": self.shift1.id}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that shift was deleted
        try:
            Shift.objects.get(pk=self.shift1.id)
            self.assertTrue(False)
        except Shift.DoesNotExist:
            self.assertTrue(True)

        # check that other shift was not deleted
        try:
            Shift.objects.get(pk=self.shift2.id)
        except Shift.DoesNotExist:
            self.assertTrue(False)
