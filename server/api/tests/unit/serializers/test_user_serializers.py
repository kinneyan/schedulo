from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from ....serializers.users import LoginUserSerializer, RegisterUserSerializer
from ....models import User


class LoginUserSerializerTest(TestCase):
    """Test cases for LoginUserSerializer"""

    def setUp(self):
        """Store the LoginUserSerializer class for use in each test."""
        self.serializer_class = LoginUserSerializer

    def test_login_serializer_valid_data(self):
        """Test serializer with valid login data"""
        data = {"email": "test@example.com", "password": "password123"}

        serializer = self.serializer_class(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")
        self.assertEqual(serializer.validated_data["password"], "password123")

    def test_login_serializer_missing_email(self):
        """Test serializer validation when email is missing"""
        data = {"password": "password123"}

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_login_serializer_missing_password(self):
        """Test serializer validation when password is missing"""
        data = {"email": "test@example.com"}

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_login_serializer_empty_data(self):
        """Test serializer validation with empty data"""
        data = {}

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)

    def test_login_serializer_accepts_any_email_format(self):
        """Test serializer accepts any string as email for login (no format validation)"""
        data = {"email": "not-an-email", "password": "password123"}

        serializer = self.serializer_class(data=data)

        # Login serializer should accept any string as email (no email format validation)
        self.assertTrue(serializer.is_valid())

    def test_login_serializer_email_validators_removed(self):
        """Test that unique email validation is disabled for login"""
        # This tests the extra_kwargs configuration
        field = self.serializer_class().fields["email"]

        # The validators list should not include unique validation but may have default CharField validators
        # Check that unique validation is not present (our custom validators=[] should override model field validators)
        validator_names = [type(validator).__name__ for validator in field.validators]
        self.assertNotIn("EmailValidator", validator_names)
        self.assertNotIn("UniqueValidator", validator_names)

    def test_login_serializer_includes_correct_fields(self):
        """Test that serializer includes only email and password fields"""
        serializer = self.serializer_class()

        expected_fields = {"email", "password"}
        actual_fields = set(serializer.fields.keys())

        self.assertEqual(expected_fields, actual_fields)

    @patch("api.models.User")
    def test_login_serializer_with_model_mock(self, mock_user_model):
        """Test serializer behavior with mocked User model"""
        data = {"email": "test@example.com", "password": "password123"}

        serializer = self.serializer_class(data=data)

        self.assertTrue(serializer.is_valid())
        # Serializer should work independently of actual User model


class RegisterUserSerializerTest(TestCase):
    """Test cases for RegisterUserSerializer"""

    def setUp(self):
        """Store the RegisterUserSerializer class for use in each test."""
        self.serializer_class = RegisterUserSerializer

    def test_register_serializer_valid_data(self):
        """Test serializer with valid registration data"""
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
        }

        serializer = self.serializer_class(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "newuser@example.com")
        self.assertEqual(serializer.validated_data["first_name"], "John")
        self.assertEqual(serializer.validated_data["last_name"], "Doe")
        self.assertEqual(serializer.validated_data["phone"], "1234567890")

    def test_register_serializer_missing_required_email(self):
        """Test serializer validation when required email is missing"""
        data = {
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_register_serializer_missing_required_password(self):
        """Test serializer validation when required password is missing"""
        data = {
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_register_serializer_missing_required_first_name(self):
        """Test serializer validation when required first_name is missing"""
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "last_name": "Doe",
            "phone": "1234567890",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_register_serializer_missing_required_last_name(self):
        """Test serializer validation when required last_name is missing"""
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "phone": "1234567890",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("last_name", serializer.errors)

    def test_register_serializer_missing_required_phone(self):
        """Test serializer validation when required phone is missing"""
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)

    def test_register_serializer_invalid_email_format(self):
        """Test serializer with invalid email format"""
        data = {
            "email": "invalid-email-format",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_register_serializer_password_write_only(self):
        """Test that password field is write-only"""
        field = self.serializer_class().fields["password"]

        self.assertTrue(field.write_only)

    def test_register_serializer_includes_correct_fields(self):
        """Test that serializer includes all required fields"""
        serializer = self.serializer_class()

        expected_fields = {"email", "password", "first_name", "last_name", "phone"}
        actual_fields = set(serializer.fields.keys())

        self.assertEqual(expected_fields, actual_fields)

    def test_register_serializer_field_requirements(self):
        """Test that all fields are properly marked as required"""
        serializer = self.serializer_class()

        required_fields = ["email", "password", "first_name", "last_name", "phone"]

        for field_name in required_fields:
            field = serializer.fields[field_name]
            self.assertTrue(field.required, f"{field_name} should be required")

    def test_register_serializer_unique_email_validation(self):
        """Test email uniqueness validation"""
        # Create a user first
        User.objects.create_user(
            email="existing@example.com",
            password="password123",
            first_name="Existing",
            last_name="User",
            phone="1111111111",
        )

        # Try to register with same email
        data = {
            "email": "existing@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "2222222222",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_register_serializer_empty_string_values(self):
        """Test serializer with empty string values"""
        data = {
            "email": "",
            "password": "",
            "first_name": "",
            "last_name": "",
            "phone": "",
        }

        serializer = self.serializer_class(data=data)

        self.assertFalse(serializer.is_valid())
        # All fields should have validation errors
        for field in data.keys():
            self.assertIn(field, serializer.errors)

    @patch("api.models.User")
    def test_register_serializer_with_model_mock(self, mock_user_model):
        """Test serializer behavior with mocked User model"""
        data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
        }

        serializer = self.serializer_class(data=data)

        # Should validate without hitting the actual model
        self.assertTrue(serializer.is_valid())
