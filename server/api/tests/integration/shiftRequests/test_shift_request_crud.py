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
    ShiftRequest,
)

class CreateShiftRequestTests(APITestCase):
    """Integration tests for the shift request creation endpoint."""

    def setUp(self):
        """Create users, workspace, members, roles, and a set of shifts."""
        self.url = reverse("create_shift_request")
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
        self.workspace2 = Workspace.objects.create(owner=self.user4, created_by=self.user4)

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

        self.role1 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name1"
        )
        self.role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name2"
        )
        self.role3 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="test name3"
        )
        self.role4 = WorkspaceRole.objects.create(
            workspace=self.workspace2, name="test name4"
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
            open=False,
            member=self.member,
        )
        self.shift2 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time2,
            end_time=self.time3,
            role=self.role1,
            created_by=self.member,
            open=True,
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
        self.shift5 = Shift.objects.create(
            workspace=self.workspace2,
            start_time=self.time2,
            end_time=self.time3,
            role=self.role4,
            created_by=self.member4,
            open=False,
            member=self.member4,
        )

        self.client.force_authenticate(user=self.member.user)

    def test_empty_body(self):
        """Verify that an error occours when no body provided"""
        data = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_sender_shift(self):
        """Verify that an error occours when no sender shift id is provided"""
        data = {"recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_recipient(self):
        """Verify that an error occours when no recipient id is provided"""
        data = {"sender_shift_id": self.shift1.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_sender_shift(self):
        """Verify that an error occours when sender shift id is invalid"""
        data = {"sender_shift_id": 999, "recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_recipient(self):
        """Verify that an error occours when recipient id is invalid"""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": 999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_recipient_shift(self):
        """Verify that an error occours when recipient shift id is invalid"""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member2.id, "recipient_shift_id": 999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mismatched_workspaces_members(self):
        """Verify that an error occours when the sender and recipient are not in the same workspace"""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member4.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sender_shift_not_held_by_sender(self):
        """Verify that an error occours when the sender does not hold the sender shift"""
        data = {"sender_shift_id": self.shift4.id, "recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recipient_shift_not_held_by_recipient(self):
        """Verify that an error occours when the recipient does not hold the recipient shift"""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member2.id, "recipient_shift_id": self.shift3.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_sender_and_recipient(self):
        """Verify that an error occours when the sender and reciever are the same member"""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_recipient_shift(self):
        """Verify that a valid request without a recipient shift creates a shift."""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        shift_request = ShiftRequest.objects.get(pk=1)
        self.assertEqual(shift_request.workspace, self.workspace)
        self.assertEqual(shift_request.sender, self.member)
        self.assertEqual(shift_request.recipient, self.member2)
        self.assertEqual(shift_request.sender_shift, self.shift1)
        self.assertEqual(shift_request.recipient_shift, None)
        self.assertEqual(shift_request.accepted, False)
        self.assertEqual(shift_request.approved, False)

    def test_recipient_shift(self):
        """Verify that a valid request with a recipient shift creates a shift."""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member3.id, "recipient_shift_id": self.shift3.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        shift_request = ShiftRequest.objects.get(pk=1)
        self.assertEqual(shift_request.workspace, self.workspace)
        self.assertEqual(shift_request.sender, self.member)
        self.assertEqual(shift_request.recipient, self.member3)
        self.assertEqual(shift_request.sender_shift, self.shift1)
        self.assertEqual(shift_request.recipient_shift, self.shift3)
        self.assertEqual(shift_request.accepted, False)
        self.assertEqual(shift_request.approved, False)