from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from decimal import Decimal
from ....models import (
    User,
    Workspace,
    WorkspaceMember,
    WorkspaceRole,
    MemberRole,
    MemberPermissions,
)


class WorkspaceRoleModelTest(TestCase):
    """Test cases for WorkspaceRole model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.workspace = Workspace.objects.create(created_by=self.user, owner=self.user)

    def test_workspace_role_creation_with_defaults(self):
        """Test workspace role creation with default values"""
        role = WorkspaceRole.objects.create(workspace=self.workspace)

        self.assertEqual(role.workspace, self.workspace)
        self.assertEqual(role.name, "Unnamed Role")
        self.assertIsNone(role.pay_rate)
        self.assertIsNotNone(role.date_created)
        self.assertIsNotNone(role.date_modified)

    def test_workspace_role_creation_with_custom_values(self):
        """Test workspace role creation with custom values"""
        role = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Manager", pay_rate=Decimal("25.50")
        )

        self.assertEqual(role.name, "Manager")
        self.assertEqual(role.pay_rate, Decimal("25.50"))

    def test_workspace_role_pay_rate_precision(self):
        """Test workspace role pay rate decimal precision (5 digits, 2 decimal places)"""
        role = WorkspaceRole.objects.create(
            workspace=self.workspace, pay_rate=Decimal("999.99")
        )

        self.assertEqual(role.pay_rate, Decimal("999.99"))

    def test_workspace_role_cascade_delete_on_workspace(self):
        """Test that workspace role is deleted when workspace is deleted"""
        role = WorkspaceRole.objects.create(workspace=self.workspace)
        role_id = role.id

        self.workspace.delete()

        with self.assertRaises(WorkspaceRole.DoesNotExist):
            WorkspaceRole.objects.get(id=role_id)

    def test_workspace_role_string_representation(self):
        """Test workspace role string representation"""
        role = WorkspaceRole.objects.create(workspace=self.workspace, name="Test Role")

        # Should use default Django string representation
        self.assertEqual(str(role), f"WorkspaceRole object ({role.id})")


class MemberRoleModelTest(TestCase):
    """Test cases for MemberRole model"""

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

    def test_member_role_creation(self):
        """Test member role creation"""
        member_role = MemberRole.objects.create(
            workspace_role=self.role, member=self.member
        )

        self.assertEqual(member_role.workspace_role, self.role)
        self.assertEqual(member_role.member, self.member)
        self.assertIsNotNone(member_role.date_created)
        self.assertIsNotNone(member_role.date_modified)

    def test_member_role_cascade_delete_on_workspace_role(self):
        """Test that member role is deleted when workspace role is deleted"""
        member_role = MemberRole.objects.create(
            workspace_role=self.role, member=self.member
        )
        member_role_id = member_role.id

        self.role.delete()

        with self.assertRaises(MemberRole.DoesNotExist):
            MemberRole.objects.get(id=member_role_id)

    def test_member_role_cascade_delete_on_member(self):
        """Test that member role is deleted when member is deleted"""
        member_role = MemberRole.objects.create(
            workspace_role=self.role, member=self.member
        )
        member_role_id = member_role.id

        self.member.delete()

        with self.assertRaises(MemberRole.DoesNotExist):
            MemberRole.objects.get(id=member_role_id)

    def test_member_can_have_multiple_roles(self):
        """Test that a member can have multiple roles"""
        role2 = WorkspaceRole.objects.create(
            workspace=self.workspace, name="Second Role"
        )

        MemberRole.objects.create(workspace_role=self.role, member=self.member)
        MemberRole.objects.create(workspace_role=role2, member=self.member)

        member_roles = MemberRole.objects.filter(member=self.member)
        self.assertEqual(member_roles.count(), 2)


class MemberPermissionsModelTest(TestCase):
    """Test cases for MemberPermissions model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.workspace = Workspace.objects.create(created_by=self.user, owner=self.user)
        self.member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.user, added_by=self.user
        )

    def test_member_permissions_creation_with_defaults(self):
        """Test member permissions creation with default values"""
        permissions = MemberPermissions.objects.create(
            workspace=self.workspace, member=self.member
        )

        self.assertEqual(permissions.workspace, self.workspace)
        self.assertEqual(permissions.member, self.member)
        self.assertFalse(permissions.is_owner)
        self.assertFalse(permissions.manage_workspace_members)
        self.assertFalse(permissions.manage_workspace_roles)
        self.assertFalse(permissions.manage_schedules)
        self.assertFalse(permissions.manage_time_off)
        self.assertIsNotNone(permissions.date_created)
        self.assertIsNotNone(permissions.date_modified)

    def test_member_permissions_creation_with_custom_permissions(self):
        """Test member permissions creation with custom permission values"""
        permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        self.assertTrue(permissions.is_owner)
        self.assertTrue(permissions.manage_workspace_members)
        self.assertTrue(permissions.manage_workspace_roles)
        self.assertTrue(permissions.manage_schedules)
        self.assertTrue(permissions.manage_time_off)

    def test_member_permissions_owner_permissions(self):
        """Test setting up owner permissions"""
        permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        # Owner should have all permissions
        self.assertTrue(permissions.is_owner)
        self.assertTrue(permissions.manage_workspace_members)
        self.assertTrue(permissions.manage_workspace_roles)
        self.assertTrue(permissions.manage_schedules)
        self.assertTrue(permissions.manage_time_off)

    def test_member_permissions_selective_permissions(self):
        """Test setting selective permissions for non-owner"""
        permissions = MemberPermissions.objects.create(
            workspace=self.workspace,
            member=self.member,
            is_owner=False,
            manage_workspace_members=False,
            manage_workspace_roles=True,  # Only this permission
            manage_schedules=False,
            manage_time_off=False,
        )

        self.assertFalse(permissions.is_owner)
        self.assertFalse(permissions.manage_workspace_members)
        self.assertTrue(permissions.manage_workspace_roles)
        self.assertFalse(permissions.manage_schedules)
        self.assertFalse(permissions.manage_time_off)

    def test_member_permissions_one_to_one_relationship(self):
        """Test that member permissions has one-to-one relationship with member"""
        MemberPermissions.objects.create(workspace=self.workspace, member=self.member)

        # Trying to create another permissions object for the same member should fail
        with self.assertRaises(IntegrityError):
            MemberPermissions.objects.create(
                workspace=self.workspace, member=self.member
            )

    def test_member_permissions_cascade_delete_on_workspace(self):
        """Test that member permissions is deleted when workspace is deleted"""
        permissions = MemberPermissions.objects.create(
            workspace=self.workspace, member=self.member
        )
        permissions_id = permissions.id

        self.workspace.delete()

        with self.assertRaises(MemberPermissions.DoesNotExist):
            MemberPermissions.objects.get(id=permissions_id)

    def test_member_permissions_cascade_delete_on_member(self):
        """Test that member permissions is deleted when member is deleted"""
        permissions = MemberPermissions.objects.create(
            workspace=self.workspace, member=self.member
        )
        permissions_id = permissions.id

        self.member.delete()

        with self.assertRaises(MemberPermissions.DoesNotExist):
            MemberPermissions.objects.get(id=permissions_id)

    @patch("django.db.models.Model.save")
    def test_member_permissions_update_scenario(self, mock_save):
        """Test updating member permissions"""
        permissions = MemberPermissions(
            workspace=self.workspace,
            member=self.member,
            is_owner=False,
            manage_schedules=False,
        )

        # Simulate promoting user to have schedule management
        permissions.manage_schedules = True

        self.assertTrue(permissions.manage_schedules)
        self.assertFalse(permissions.is_owner)  # Other permissions unchanged
