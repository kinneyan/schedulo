from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta
from ....models import (
    User,
    Workspace,
    WorkspaceMember,
    WorkspaceRole,
    Shift,
    ShiftRequest,
    TimeOffRequest,
    Unavailability,
)


class ShiftModelTest(TestCase):
    """Test cases for Shift model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.workspace = Workspace.objects.create(created_by=self.user, owner=self.user)
        self.member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.user, added_by=self.user
        )
        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Test Role"
        )

    def test_shift_creation_with_member(self):
        """Test shift creation with assigned member"""
        start_time = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone())
        end_time = datetime(2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone())

        shift = Shift.objects.create(
            member=self.member,
            workspace=self.workspace,
            start_time=start_time,
            end_time=end_time,
            role=self.role,
            created_by=self.member,
        )

        self.assertEqual(shift.member, self.member)
        self.assertEqual(shift.workspace, self.workspace)
        self.assertEqual(shift.start_time, start_time)
        self.assertEqual(shift.end_time, end_time)
        self.assertEqual(shift.role, self.role)
        self.assertEqual(shift.created_by, self.member)
        self.assertFalse(shift.open)

    def test_shift_creation_open_shift(self):
        """Test creation of open shift (no assigned member)"""
        start_time = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone())
        end_time = datetime(2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone())

        shift = Shift.objects.create(
            member=None,
            workspace=self.workspace,
            start_time=start_time,
            end_time=end_time,
            role=self.role,
            created_by=self.member,
            open=True,
        )

        self.assertIsNone(shift.member)
        self.assertTrue(shift.open)

    def test_shift_cascade_delete_on_workspace(self):
        """Test that shift is deleted when workspace is deleted"""
        shift = Shift.objects.create(
            workspace=self.workspace,
            start_time=datetime(
                2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone()
            ),
            end_time=datetime(
                2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone()
            ),
            role=self.role,
            created_by=self.member,
        )
        shift_id = shift.id

        self.workspace.delete()

        with self.assertRaises(Shift.DoesNotExist):
            Shift.objects.get(id=shift_id)


class ShiftRequestModelTest(TestCase):
    """Test cases for ShiftRequest model"""

    def setUp(self):
        self.sender_user = User.objects.create_user(
            email="sender@example.com", password="password123"
        )
        self.recipient_user = User.objects.create_user(
            email="recipient@example.com", password="password123"
        )
        self.workspace = Workspace.objects.create(
            created_by=self.sender_user, owner=self.sender_user
        )
        self.sender_member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.sender_user, added_by=self.sender_user
        )
        self.recipient_member = WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.recipient_user,
            added_by=self.sender_user,
        )
        self.role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Test Role"
        )
        self.sender_shift = Shift.objects.create(
            member=self.sender_member,
            workspace=self.workspace,
            start_time=datetime(
                2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone()
            ),
            end_time=datetime(
                2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone()
            ),
            role=self.role,
            created_by=self.sender_member,
        )

    def test_shift_request_creation(self):
        """Test shift request creation"""
        shift_request = ShiftRequest.objects.create(
            sender=self.sender_member,
            recipient=self.recipient_member,
            sender_shift=self.sender_shift,
        )

        self.assertEqual(shift_request.sender, self.sender_member)
        self.assertEqual(shift_request.recipient, self.recipient_member)
        self.assertEqual(shift_request.sender_shift, self.sender_shift)
        self.assertIsNone(shift_request.recipient_shift)
        self.assertFalse(shift_request.accepted)
        self.assertFalse(shift_request.approved)

    def test_shift_request_with_recipient_shift(self):
        """Test shift request with recipient shift (swap)"""
        recipient_shift = Shift.objects.create(
            member=self.recipient_member,
            workspace=self.workspace,
            start_time=datetime(
                2025, 1, 2, 9, 0, tzinfo=timezone.get_default_timezone()
            ),
            end_time=datetime(
                2025, 1, 2, 17, 0, tzinfo=timezone.get_default_timezone()
            ),
            role=self.role,
            created_by=self.recipient_member,
        )

        shift_request = ShiftRequest.objects.create(
            sender=self.sender_member,
            recipient=self.recipient_member,
            sender_shift=self.sender_shift,
            recipient_shift=recipient_shift,
        )

        self.assertEqual(shift_request.recipient_shift, recipient_shift)


class TimeOffRequestModelTest(TestCase):
    """Test cases for TimeOffRequest model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.approver_user = User.objects.create_user(
            email="approver@example.com", password="password123"
        )
        self.workspace = Workspace.objects.create(created_by=self.user, owner=self.user)
        self.member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.user, added_by=self.user
        )
        self.approver_member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.approver_user, added_by=self.user
        )

    def test_time_off_request_creation(self):
        """Test time off request creation"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 5)

        time_off = TimeOffRequest.objects.create(
            member=self.member,
            workspace=self.workspace,
            start_date=start_date,
            end_date=end_date,
            reason="Vacation",
        )

        self.assertEqual(time_off.member, self.member)
        self.assertEqual(time_off.workspace, self.workspace)
        self.assertEqual(time_off.start_date, start_date)
        self.assertEqual(time_off.end_date, end_date)
        self.assertEqual(time_off.reason, "Vacation")
        self.assertFalse(time_off.approved)
        self.assertIsNone(time_off.approved_by)

    def test_time_off_request_with_approval(self):
        """Test time off request with approval"""
        time_off = TimeOffRequest.objects.create(
            member=self.member,
            workspace=self.workspace,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 5),
            approved=True,
            approved_by=self.approver_member,
        )

        self.assertTrue(time_off.approved)
        self.assertEqual(time_off.approved_by, self.approver_member)


class UnavailabilityModelTest(TestCase):
    """Test cases for Unavailability model and its constraints"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.workspace = Workspace.objects.create(created_by=self.user, owner=self.user)
        self.member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.user, added_by=self.user
        )

    def test_unavailability_creation_valid_day(self):
        """Test unavailability creation with valid day of week"""
        for day in range(7):  # 0-6 are valid
            unavailability = Unavailability.objects.create(
                member=self.member,
                start_time=datetime(
                    2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone()
                ),
                end_time=datetime(
                    2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone()
                ),
                day_of_week=day,
            )

            self.assertEqual(unavailability.day_of_week, day)
            unavailability.delete()  # Clean up for next iteration

    def test_unavailability_invalid_day_of_week_negative(self):
        """Test that day_of_week < 0 raises validation error"""
        with self.assertRaises(ValidationError):
            unavailability = Unavailability(
                member=self.member,
                start_time=datetime(
                    2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone()
                ),
                end_time=datetime(
                    2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone()
                ),
                day_of_week=-1,
            )
            unavailability.full_clean()

    def test_unavailability_invalid_day_of_week_too_high(self):
        """Test that day_of_week > 6 raises validation error"""
        with self.assertRaises(ValidationError):
            unavailability = Unavailability(
                member=self.member,
                start_time=datetime(
                    2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone()
                ),
                end_time=datetime(
                    2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone()
                ),
                day_of_week=7,
            )
            unavailability.full_clean()

    @patch("django.db.models.Model.save")
    def test_unavailability_day_of_week_constraint_at_db_level(self, mock_save):
        """Test that database constraint exists for day_of_week"""
        # This tests that the constraint is properly defined in the model
        Unavailability(
            member=self.member,
            start_time=datetime(
                2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone()
            ),
            end_time=datetime(
                2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone()
            ),
            day_of_week=5,
        )

        # Check that the constraint is defined in Meta
        constraints = Unavailability._meta.constraints
        self.assertEqual(len(constraints), 1)
        self.assertEqual(constraints[0].name, "day_of_week_valid")

    def test_unavailability_time_fields(self):
        """Test unavailability time field handling"""
        start_time = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone())
        end_time = datetime(2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone())

        unavailability = Unavailability.objects.create(
            member=self.member, start_time=start_time, end_time=end_time, day_of_week=1
        )

        self.assertEqual(unavailability.start_time, start_time)
        self.assertEqual(unavailability.end_time, end_time)

    def test_unavailability_cascade_delete_on_member(self):
        """Test that unavailability is deleted when member is deleted"""
        unavailability = Unavailability.objects.create(
            member=self.member,
            start_time=datetime(
                2025, 1, 1, 9, 0, tzinfo=timezone.get_default_timezone()
            ),
            end_time=datetime(
                2025, 1, 1, 17, 0, tzinfo=timezone.get_default_timezone()
            ),
            day_of_week=1,
        )
        unavailability_id = unavailability.id

        self.member.delete()

        with self.assertRaises(Unavailability.DoesNotExist):
            Unavailability.objects.get(id=unavailability_id)
