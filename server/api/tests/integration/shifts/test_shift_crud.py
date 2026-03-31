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

        self.role = WorkspaceRole.objects.create(workspace=self.workspace, name="test name")

        self.time1 = datetime.now(timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)

        self.client.force_authenticate(user=self.member.user)
        self.url = reverse("workspace_shifts", kwargs={"workspace_id": self.workspace.id})

    def test_invalid_workspace(self):
        """Verify that a non-existent workspace_id returns a 404 error."""
        url = reverse("workspace_shifts", kwargs={"workspace_id": 999})
        data = {
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_role(self):
        """Verify that omitting role_id returns a 400 error."""
        data = {"start_time": self.time1, "end_time": self.time2}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        """Verify that a non-existent role_id returns a 404 error."""
        data = {"role_id": 999, "start_time": self.time1, "end_time": self.time2}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_time(self):
        """Verify that omitting start_time and end_time returns a 400 error."""
        data = {"role_id": self.role.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_time_before_start(self):
        """Verify that an end_time earlier than start_time returns a 400 error."""
        data = {
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
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Shift.objects.filter(workspace=self.workspace, role=self.role).exists())

    def test_valid(self):
        """Verify that a valid payload creates a shift and returns 201."""
        data = {
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Shift.objects.filter(
                workspace=self.workspace,
                role=self.role,
                start_time=self.time1,
                end_time=self.time2,
                open=True,
            ).exists()
        )

    def test_with_member(self):
        """Verify that providing a member_id creates an assigned (non-open) shift."""
        data = {
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
            "member_id": self.member2.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Shift.objects.filter(
                workspace=self.workspace,
                role=self.role,
                start_time=self.time1,
                end_time=self.time2,
                open=False,
                member=self.member2,
            ).exists()
        )

    def test_with_invalid_member(self):
        """Verify that a non-existent member_id returns a 404 and no shift is created."""
        data = {
            "role_id": self.role.id,
            "start_time": self.time1,
            "end_time": self.time2,
            "member_id": 999,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Shift.objects.filter(workspace=self.workspace, role=self.role).exists())


class GetShiftTests(APITestCase):
    """Integration tests for the get shift endpoint."""

    def setUp(self):
        """Create a workspace with members, roles, and shifts."""
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
            workspace=self.workspace, name="Test Role", pay_rate=15.00
        )

        self.shift = Shift.objects.create(
            workspace=self.workspace,
            member=self.member,
            role=self.role,
            created_by=self.member,
            start_time="2026-01-01T09:00:00Z",
            end_time="2026-01-01T17:00:00Z",
        )
        self.open_shift = Shift.objects.create(
            workspace=self.workspace,
            member=None,
            role=self.role,
            created_by=self.member,
            start_time="2026-01-02T09:00:00Z",
            end_time="2026-01-02T17:00:00Z",
            open=True,
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse("shift", kwargs={"shift_id": self.shift.id})

    def test_invalid_shift(self):
        """Verify that a nonexistent shift_id returns 404."""
        url = reverse("shift", kwargs={"shift_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_shift_as_non_member(self):
        """Verify that a user who is not a workspace member receives 403."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_shift_valid(self):
        """Verify that a workspace member can retrieve shift details with correct structure."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertEqual(result["id"], self.shift.id)
        self.assertEqual(result["member"]["id"], self.member.id)
        self.assertEqual(result["member"]["first_name"], self.user.first_name)
        self.assertEqual(result["member"]["last_name"], self.user.last_name)
        self.assertEqual(result["role"]["id"], self.role.id)
        self.assertEqual(result["role"]["name"], self.role.name)
        self.assertEqual(result["start_time"], self.shift.start_time)
        self.assertEqual(result["end_time"], self.shift.end_time)
        self.assertEqual(result["open"], self.shift.open)

    def test_get_shift_valid_as_unprivileged_member(self):
        """Verify that a member without manage_schedules permission can still retrieve shift details."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_open_shift_valid(self):
        """Verify that an open shift with no assigned member returns None for member field."""
        url = reverse("shift", kwargs={"shift_id": self.open_shift.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["result"]
        self.assertIsNone(result["member"])
        self.assertTrue(result["open"])


class ModifyShiftTests(APITestCase):
    """Integration tests for the shift modification endpoint."""

    def setUp(self):
        """Create users, workspace, members with permissions, roles, and an existing shift."""
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
        self.url = reverse("shift", kwargs={"shift_id": self.shift.id})

    def test_invalid_shift(self):
        """Verify that a non-existent shift_id returns a 404 error."""
        url = reverse("shift", kwargs={"shift_id": 999})
        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_without_permissions(self):
        """Verify that a member without manage_schedules permission cannot modify a shift."""
        self.client.force_authenticate(user=self.member2.user)
        data = {"start_time": self.time4, "end_time": self.time3}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            ).exists()
        )

    def test_modify_cross_workspace_isolation(self):
        """Verify that a privileged member of another workspace cannot modify a shift in this workspace."""
        other_workspace = Workspace.objects.create(owner=self.user3, created_by=self.user3)
        other_member = WorkspaceMember.objects.create(
            user=self.user3, workspace=other_workspace, added_by=self.user3
        )
        MemberPermissions.objects.create(
            workspace=other_workspace,
            member=other_member,
            is_owner=True,
            manage_schedules=True,
        )
        self.client.force_authenticate(user=self.user3)

        response = self.client.put(
            self.url, {"start_time": self.time4, "end_time": self.time3}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            ).exists()
        )

    def test_invalid_start_and_end(self):
        """Verify that non-datetime start_time and end_time values return a 400 error."""
        data = {"start_time": 100, "end_time": 100}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            ).exists()
        )

    def test_invalid_start_and_end_order(self):
        """Verify that a start_time after end_time returns a 400 error."""
        data = {"start_time": self.time3, "end_time": self.time4}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            ).exists()
        )

    def test_invalid_start(self):
        """Verify that a new start_time after the existing end_time returns a 400 error."""
        data = {"start_time": self.time3}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            ).exists()
        )

    def test_invalid_end(self):
        """Verify that a new end_time before the existing start_time returns a 400 error."""
        data = {"end_time": self.time4}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time1, end_time=self.time2
            ).exists()
        )

    def test_valid_start_and_end(self):
        """Verify that updating both start_time and end_time succeeds and persists the changes."""
        data = {"start_time": self.time4, "end_time": self.time3}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time4, end_time=self.time3
            ).exists()
        )

    def test_valid_start(self):
        """Verify that updating only start_time succeeds and persists the change."""
        data = {"start_time": self.time4}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time4, end_time=self.time2
            ).exists()
        )

    def test_valid_end(self):
        """Verify that updating only end_time succeeds and persists the change."""
        data = {"end_time": self.time3}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id, start_time=self.time1, end_time=self.time3
            ).exists()
        )

    def test_invalid_member(self):
        """Verify that a non-existent member_id returns a 404 and the shift is unchanged."""
        data = {"member_id": 999}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Shift.objects.filter(pk=self.shift.id, open=True).exists())

    def test_valid_member(self):
        """Verify that assigning a valid member marks the shift as non-open."""
        data = {"member_id": self.member.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Shift.objects.filter(pk=self.shift.id, member=self.member, open=False).exists()
        )

    def test_invalid_role(self):
        """Verify that a non-existent role_id returns a 404 and the shift role is unchanged."""
        data = {"role_id": 999}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Shift.objects.filter(pk=self.shift.id, role=self.role).exists())

    def test_valid_role(self):
        """Verify that updating to a valid role_id succeeds and persists the change."""
        data = {"role_id": self.role2.id}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Shift.objects.filter(pk=self.shift.id, role=self.role2).exists())

    def test_modify_multiple(self):
        """Verify that updating role, member, and times together all persist correctly."""
        data = {
            "role_id": self.role2.id,
            "member_id": self.member2.id,
            "start_time": self.time4,
            "end_time": self.time3,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Shift.objects.filter(
                pk=self.shift.id,
                role=self.role2,
                member=self.member2,
                start_time=self.time4,
                end_time=self.time3,
            ).exists()
        )


class DeleteShiftTests(APITestCase):
    """Integration tests for the shift deletion endpoint."""

    def setUp(self):
        """Create users, workspace, members with permissions, roles, and two existing shifts."""
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

        self.role = WorkspaceRole.objects.create(workspace=self.workspace, name="test name")

        self.time1 = datetime.now(timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)
        self.time3 = self.time1 + timedelta(hours=4)

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
        self.url = reverse("shift", kwargs={"shift_id": self.shift1.id})

    def test_invalid_shift(self):
        """Verify that a non-existent shift_id returns a 404 error."""
        url = reverse("shift", kwargs={"shift_id": 999})
        response = self.client.delete(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_without_permissions(self):
        """Verify that a member without manage_schedules permission cannot delete a shift."""
        self.client.force_authenticate(user=self.member2.user)
        response = self.client.delete(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Shift.objects.filter(pk=self.shift1.id).exists())

    def test_valid(self):
        """Verify that a valid delete request removes the target shift and leaves others intact."""
        response = self.client.delete(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Shift.objects.filter(pk=self.shift1.id).exists())
        self.assertTrue(Shift.objects.filter(pk=self.shift2.id).exists())

    def test_delete_cross_workspace_isolation(self):
        """Verify that a privileged member of another workspace cannot delete a shift in this workspace."""
        other_workspace = Workspace.objects.create(owner=self.user3, created_by=self.user3)
        other_member = WorkspaceMember.objects.create(
            user=self.user3, workspace=other_workspace, added_by=self.user3
        )
        MemberPermissions.objects.create(
            workspace=other_workspace,
            member=other_member,
            is_owner=True,
            manage_schedules=True,
        )
        self.client.force_authenticate(user=self.user3)

        response = self.client.delete(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Shift.objects.filter(pk=self.shift1.id).exists())
