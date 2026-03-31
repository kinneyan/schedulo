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
    """Integration tests for the member shift request creation endpoint."""

    def setUp(self):
        """Create users, workspace, members, roles, and a set of shifts."""
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
            user=self.user3, workspace=self.workspace, added_by=self.user
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

        self.role1 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name1")
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name2")
        self.role3 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name3")
        self.role4 = WorkspaceRole.objects.create(workspace=self.workspace2, name="test name4")

        self.time1 = datetime(2025, 2, 16, tzinfo=timezone.utc)
        self.time2 = self.time1 + timedelta(hours=2)
        self.time3 = self.time1 + timedelta(hours=4)

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

        self.client.force_authenticate(user=self.user)
        self.url = reverse("member_shift_request", kwargs={"member_id": self.member.id})

    def test_empty_body(self):
        """Verify that an error occurs when no body is provided."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_sender_shift(self):
        """Verify that an error occurs when no sender shift id is provided."""
        data = {"recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_recipient(self):
        """Verify that an error occurs when no recipient id is provided."""
        data = {"sender_shift_id": self.shift1.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_member_id(self):
        """Verify that a nonexistent member_id in the url returns 404."""
        url = reverse("member_shift_request", kwargs={"member_id": 999})
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member2.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_sender_not_request_user(self):
        """Verify that a user cannot create a shift request on behalf of another member."""
        url = reverse("member_shift_request", kwargs={"member_id": self.member2.id})
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member3.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_recipient(self):
        """Verify that an error occurs when recipient id is invalid."""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": 999}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_sender_shift(self):
        """Verify that an error occurs when sender shift id is invalid."""
        data = {"sender_shift_id": 999, "recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_recipient_shift(self):
        """Verify that an error occurs when recipient shift id is invalid."""
        data = {
            "sender_shift_id": self.shift1.id,
            "recipient_id": self.member2.id,
            "recipient_shift_id": 999,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_same_sender_and_recipient(self):
        """Verify that an error occurs when the sender and recipient are the same member."""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mismatched_workspaces_members(self):
        """Verify that an error occurs when the sender and recipient are not in the same workspace."""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member4.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sender_shift_not_held_by_sender(self):
        """Verify that an error occurs when the sender does not hold the sender shift."""
        data = {"sender_shift_id": self.shift4.id, "recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recipient_shift_not_held_by_recipient(self):
        """Verify that an error occurs when the recipient does not hold the recipient shift."""
        data = {
            "sender_shift_id": self.shift1.id,
            "recipient_id": self.member2.id,
            "recipient_shift_id": self.shift3.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_shift_request_no_recipient_shift(self):
        """Verify that a valid request without a recipient shift creates a shift request."""
        data = {"sender_shift_id": self.shift1.id, "recipient_id": self.member2.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        shift_request = ShiftRequest.objects.get(sender=self.member, recipient=self.member2)
        self.assertEqual(shift_request.workspace, self.workspace)
        self.assertEqual(shift_request.sender, self.member)
        self.assertEqual(shift_request.recipient, self.member2)
        self.assertEqual(shift_request.sender_shift, self.shift1)
        self.assertIsNone(shift_request.recipient_shift)
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.PENDING)
        self.assertEqual(shift_request.approved, ShiftRequest.Status.PENDING)

    def test_create_shift_request_with_recipient_shift(self):
        """Verify that a valid request with a recipient shift creates a shift request."""
        data = {
            "sender_shift_id": self.shift1.id,
            "recipient_id": self.member3.id,
            "recipient_shift_id": self.shift3.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        shift_request = ShiftRequest.objects.get(sender=self.member, recipient=self.member3)
        self.assertEqual(shift_request.workspace, self.workspace)
        self.assertEqual(shift_request.sender, self.member)
        self.assertEqual(shift_request.recipient, self.member3)
        self.assertEqual(shift_request.sender_shift, self.shift1)
        self.assertEqual(shift_request.recipient_shift, self.shift3)
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.PENDING)
        self.assertEqual(shift_request.approved, ShiftRequest.Status.PENDING)


class ShiftRequestRespondTests(APITestCase):
    """Integration tests for the shift request respond endpoint."""

    def setUp(self):
        """Create users, workspace, members, roles, and a set of shifts."""
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
        self.user5 = User.objects.create_user(
            email="testuser5@example.com",
            password="testpassword",
            first_name="Test5",
            last_name="User5",
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
            user=self.user3, workspace=self.workspace, added_by=self.user
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
            user=self.user4, workspace=self.workspace, added_by=self.user
        )
        self.permissions4 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member4,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.member5 = WorkspaceMember.objects.create(
            user=self.user5, workspace=self.workspace, added_by=self.user
        )
        self.permissions5 = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member5,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.role1 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name1")
        self.role2 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name2")
        self.role3 = WorkspaceRole.objects.create(workspace=self.workspace, name="test name3")

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
            start_time=self.time4,
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
            workspace=self.workspace,
            start_time=self.time2,
            end_time=self.time3,
            role=self.role1,
            created_by=self.member,
            open=False,
            member=self.member4,
        )
        self.shift6 = Shift.objects.create(
            workspace=self.workspace,
            start_time=self.time1,
            end_time=self.time3,
            role=self.role1,
            created_by=self.member,
            open=False,
            member=self.member5,
        )

    def test_missing_accept(self):
        """Verify that a request without accept returns 400."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member2,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member2.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_shift_request_id(self):
        """Verify that a request with an invalid shift request id returns 404."""
        self.client.force_authenticate(user=self.member2.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": 999})
        data = {"accept": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_accept(self):
        """Verify that a request with an invalid accept value returns 400."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member2,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member2.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": "notbool"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_not_as_recipient(self):
        """Verify that a request cannot be accepted by a member other than the recipient."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member2,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member3.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.PENDING)

    def test_decline_not_as_recipient(self):
        """Verify that a request cannot be declined by a member other than the recipient."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member2,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member3.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": False}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.PENDING)

    def test_valid_accept(self):
        """Verify that a valid request with no overlap and no recipient shift can be accepted."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member2,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member2.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.ACCEPTED)

    def test_adjacent(self):
        """Verify that a request with adjacent shifts can be accepted (adjacent shifts don't count as overlap)."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member4,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member4.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.ACCEPTED)

    def test_swap_overlap(self):
        """Verify that a swap request where the recipient shift overlaps with the sender shift can be accepted."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member5,
            sender_shift=self.shift1,
            recipient_shift=self.shift6,
        )
        self.client.force_authenticate(user=self.member5.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.ACCEPTED)

    def test_overlap(self):
        """Verify that a request with an overlapping shift cannot be accepted."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member3,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member3.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"]["message"],
            "Recipient cannot accept shift that overlaps with another shift they have.",
        )

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.PENDING)

    def test_valid_decline(self):
        """Verify that a valid request can be declined."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member2,
            sender_shift=self.shift1,
        )
        self.client.force_authenticate(user=self.member2.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": False}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.DECLINED)

    def test_accept_after_decline(self):
        """Verify that a request cannot be accepted after being declined."""
        shift_request = ShiftRequest.objects.create(
            workspace=self.workspace,
            sender=self.member,
            recipient=self.member2,
            sender_shift=self.shift1,
            accepted=ShiftRequest.Status.DECLINED,
        )
        self.client.force_authenticate(user=self.member2.user)
        url = reverse("shift_request_respond", kwargs={"shift_request_id": shift_request.id})
        data = {"accept": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        shift_request.refresh_from_db()
        self.assertEqual(shift_request.accepted, ShiftRequest.Status.DECLINED)
