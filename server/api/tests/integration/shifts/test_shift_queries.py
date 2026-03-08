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


class GetShiftsTest(APITestCase):
    """Integration tests for the get shifts query endpoint."""

    def setUp(self):
        """Create users, workspace, members, roles, and a set of shifts for filtering tests."""
        self.url = reverse("get_shifts")
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
            user=self.user2, workspace=self.workspace, added_by=self.user
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

        self.role1 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name1"
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name2"
        )
        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name3"
        )

        self.time1 = datetime(2025, 2, 16, tzinfo=timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)
        self.time3 = self.time1 + timedelta(hours=4)
        self.time4 = self.time1 - timedelta(hours=2)
        self.time5 = self.time1 + timedelta(days=5)
        self.time6 = self.time1 + timedelta(days=5) + timedelta(hours=2)

        self.shift1 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time1,
            end_time=self.time2,
            role=self.role1,
            created_by=self.member,
            open=True,
        )
        self.shift2 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time2,
            end_time=self.time3,
            role=self.role1,
            created_by=self.member,
            open=False,
            member=self.member2,
        )
        self.shift3 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time2,
            end_time=self.time3,
            role=self.role1,
            created_by=self.member,
            open=False,
            member=self.member3,
        )
        self.shift4 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time2,
            end_time=self.time3,
            role=self.role2,
            created_by=self.member,
            open=False,
            member=self.member3,
        )

        self.client.force_authenticate(user=self.member.user)

    def test_member(self):
        """Verify that filtering by member_id returns only that member's shifts."""
        data = {"member_id": self.member3.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that response has correct shifts
        self.assertEqual(len(response.data["shifts"]), 2)
        shifts = response.data["shifts"]
        self.assertEqual(shifts[0]["id"], self.shift3.id)
        self.assertEqual(shifts[1]["id"], self.shift4.id)

    def test_member_and_role(self):
        """Verify that filtering by both member_id and role_id narrows results correctly."""
        data = {"member_id": self.member3.id, "role_id": self.role2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that response has correct shifts
        self.assertEqual(len(response.data["shifts"]), 1)
        shifts = response.data["shifts"]
        self.assertEqual(shifts[0]["id"], self.shift4.id)

    def test_date_range_invalid(self):
        """Verify that malformed date range values return a 400 error."""
        data = {"range_start": 999, "range_end": "999"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_date_range(self):
        """Verify that providing both range_start and range_end returns only shifts within that window."""
        # add new shift
        self.shift5 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time5,
            end_time=self.time6,
            role=self.role2,
            created_by=self.member,
            open=False,
            member=self.member3,
        )

        data = {"range_start": self.time5.date(), "range_end": self.time5.date()}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that response has correct shifts
        self.assertEqual(len(response.data["shifts"]), 1)
        shifts = response.data["shifts"]
        self.assertEqual(shifts[0]["id"], self.shift5.id)

    def test_date_range_only_start(self):
        """Verify that providing only range_start returns shifts on or after that date."""
        # add new shift
        self.shift5 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time5,
            end_time=self.time6,
            role=self.role2,
            created_by=self.member,
            open=False,
            member=self.member3,
        )

        data = {"range_start": (self.time1 + timedelta(days=1)).date()}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that response has correct shifts
        self.assertEqual(len(response.data["shifts"]), 1)
        shifts = response.data["shifts"]
        self.assertEqual(shifts[0]["id"], self.shift5.id)

    def test_date_range_only_end(self):
        """Verify that providing only range_end returns all shifts on or before that date."""
        # add new shift
        self.shift5 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time5,
            end_time=self.time6,
            role=self.role2,
            created_by=self.member,
            open=False,
            member=self.member3,
        )

        data = {"range_end": (self.time5 + timedelta(days=1)).date()}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that response has correct shifts
        self.assertEqual(len(response.data["shifts"]), 5)
        shifts = response.data["shifts"]
        ids = [row["id"] for row in shifts]
        self.assertTrue(self.shift1.id in ids)
        self.assertTrue(self.shift2.id in ids)
        self.assertTrue(self.shift3.id in ids)
        self.assertTrue(self.shift4.id in ids)
        self.assertTrue(self.shift5.id in ids)

    def test_within_user_workspaces(self):
        """Verify that shifts from workspaces the requester does not belong to are excluded."""
        self.workspace2 = Workspace.objects.create(
            owner=self.user4, created_by=self.user4
        )

        self.member4 = WorkspaceMember.objects.create(
            user=self.user4, workspace=self.workspace2, added_by=self.user4
        )
        self.permissions4 = MemberPermissions.objects.create(
            workspace=self.workspace2,
            member=self.member4,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace2, name="test name3"
        )

        self.shift5 = Shift.objects.create(
            workspace=self.workspace2,
            start_time=self.time1,
            end_time=self.time2,
            role=self.role3,
            created_by=self.member4,
            open=True,
        )

        data = {"member_id": self.member4.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that response has correct shifts
        self.assertEqual(len(response.data["shifts"]), 0)
