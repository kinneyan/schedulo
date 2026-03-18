from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ....models import CustomUserManager, User, Workspace, WorkspaceMember


class CustomUserManagerTest(TestCase):
    """Test cases for CustomUserManager methods"""

    def setUp(self):
        """Set up a bare CustomUserManager instance with the User model attached."""
        self.manager = CustomUserManager()
        self.manager.model = User

    def test_create_user_without_email_raises_error(self):
        """Test that create_user raises ValueError when email is not provided"""
        with self.assertRaises(ValueError) as context:
            self.manager.create_user("", "password123")

        self.assertEqual(str(context.exception), "The Email field must be set")

        with self.assertRaises(ValueError) as context:
            self.manager.create_user(None, "password123")

        self.assertEqual(str(context.exception), "The Email field must be set")

    def test_create_superuser_with_is_staff_false_raises_error(self):
        """Test that create_superuser raises ValueError if is_staff=False"""
        with self.assertRaises(ValueError) as context:
            self.manager.create_superuser(
                "admin@example.com", "password123", is_staff=False
            )

        self.assertEqual(str(context.exception), "Superuser must have is_staff=True.")

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        """Test that create_superuser raises ValueError if is_superuser=False"""
        with self.assertRaises(ValueError) as context:
            self.manager.create_superuser(
                "admin@example.com", "password123", is_superuser=False
            )

        self.assertEqual(
            str(context.exception), "Superuser must have is_superuser=True."
        )


class UserModelTest(TestCase):
    """Test cases for User model"""

    def test_user_creation_with_required_fields(self):
        """Test creating user with required fields"""
        user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.check_password("password123"))
        self.assertIsNone(user.username)

    def test_user_creation_with_phone(self):
        """Test creating user with phone number"""
        user = User.objects.create_user(
            email="test@example.com", password="password123", phone="1234567890"
        )

        self.assertEqual(user.phone, "1234567890")

    def test_user_email_unique_constraint(self):
        """Test that email field has unique constraint"""
        User.objects.create_user(email="test@example.com", password="password123")

        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            User.objects.create_user(email="test@example.com", password="password456")

    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        # Default Django behavior should use email since username is None
        self.assertIn("test@example.com", str(user))


class WorkspaceModelTest(TestCase):
    """Test cases for Workspace model"""

    def setUp(self):
        """Create an owner user for use in each workspace test."""
        self.user = User.objects.create_user(
            email="owner@example.com", password="password123"
        )

    def test_workspace_creation_with_defaults(self):
        """Test workspace creation with default values"""
        workspace = Workspace.objects.create(created_by=self.user, owner=self.user)

        self.assertEqual(workspace.created_by, self.user)
        self.assertEqual(workspace.owner, self.user)
        self.assertEqual(workspace.name, "Unnamed Workspace")
        self.assertIsNotNone(workspace.date_created)
        self.assertIsNotNone(workspace.date_modified)

    def test_workspace_creation_with_custom_name(self):
        """Test workspace creation with custom name"""
        workspace = Workspace.objects.create(
            created_by=self.user, owner=self.user, name="My Custom Workspace"
        )

        self.assertEqual(workspace.name, "My Custom Workspace")

    def test_workspace_owner_cascade_delete(self):
        """Test that workspace is deleted when owner is deleted"""
        workspace = Workspace.objects.create(created_by=self.user, owner=self.user)
        workspace_id = workspace.id

        self.user.delete()

        with self.assertRaises(Workspace.DoesNotExist):
            Workspace.objects.get(id=workspace_id)


class WorkspaceMemberModelTest(TestCase):
    """Test cases for WorkspaceMember model"""

    def setUp(self):
        """Create owner, member user, and workspace for use in each test."""
        self.owner = User.objects.create_user(
            email="owner@example.com", password="password123"
        )
        self.member_user = User.objects.create_user(
            email="member@example.com", password="password123"
        )
        self.workspace = Workspace.objects.create(
            created_by=self.owner, owner=self.owner
        )

    def test_workspace_member_creation(self):
        """Test workspace member creation"""
        member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.member_user, added_by=self.owner
        )

        self.assertEqual(member.workspace, self.workspace)
        self.assertEqual(member.user, self.member_user)
        self.assertEqual(member.added_by, self.owner)
        self.assertIsNone(member.pay_rate)
        self.assertIsNotNone(member.date_created)

    def test_workspace_member_with_pay_rate(self):
        """Test workspace member creation with pay rate"""
        member = WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.member_user,
            added_by=self.owner,
            pay_rate=15.50,
        )

        self.assertEqual(member.pay_rate, 15.50)

    def test_workspace_member_cascade_delete_on_workspace(self):
        """Test that workspace member is deleted when workspace is deleted"""
        member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.member_user, added_by=self.owner
        )
        member_id = member.id

        self.workspace.delete()

        with self.assertRaises(WorkspaceMember.DoesNotExist):
            WorkspaceMember.objects.get(id=member_id)

    def test_workspace_member_cascade_delete_on_user(self):
        """Test that workspace member is deleted when user is deleted"""
        member = WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.member_user, added_by=self.owner
        )
        member_id = member.id

        self.member_user.delete()

        with self.assertRaises(WorkspaceMember.DoesNotExist):
            WorkspaceMember.objects.get(id=member_id)
