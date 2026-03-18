from django.test import TestCase
from ....serializers.users import LoginUserSerializer, RegisterUserSerializer
from ....models import User


class LoginUserSerializerTest(TestCase):
    """Test cases for LoginUserSerializer"""

    def setUp(self):
        self.serializer_class = LoginUserSerializer

    def test_valid_data(self):
        """Test serializer with valid login data"""
        data = {"email": "test@example.com", "password": "password123"}
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")
        self.assertEqual(serializer.validated_data["password"], "password123")

    def test_missing_email(self):
        """Test serializer validation when email is missing"""
        serializer = self.serializer_class(data={"password": "password123"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_password(self):
        """Test serializer validation when password is missing"""
        serializer = self.serializer_class(data={"email": "test@example.com"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_empty_data(self):
        """Test serializer validation with empty data"""
        serializer = self.serializer_class(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)

    def test_accepts_any_email_format(self):
        """Login serializer should accept any string as email (no format validation)"""
        serializer = self.serializer_class(
            data={"email": "not-an-email", "password": "password123"}
        )
        self.assertTrue(serializer.is_valid())


class RegisterUserSerializerTest(TestCase):
    """Test cases for RegisterUserSerializer"""

    def setUp(self):
        self.serializer_class = RegisterUserSerializer

    def test_valid_data(self):
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

    def test_missing_email(self):
        serializer = self.serializer_class(data={
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_password(self):
        serializer = self.serializer_class(data={
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_missing_first_name(self):
        serializer = self.serializer_class(data={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "last_name": "Doe",
            "phone": "1234567890",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_missing_last_name(self):
        serializer = self.serializer_class(data={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "phone": "1234567890",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("last_name", serializer.errors)

    def test_missing_phone(self):
        serializer = self.serializer_class(data={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)

    def test_invalid_email_format(self):
        serializer = self.serializer_class(data={
            "email": "invalid-email-format",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_duplicate_email(self):
        """Test email uniqueness validation"""
        User.objects.create_user(
            email="existing@example.com",
            password="password123",
            first_name="Existing",
            last_name="User",
            phone="1111111111",
        )
        serializer = self.serializer_class(data={
            "email": "existing@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "2222222222",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_empty_string_values(self):
        """All empty strings should fail validation"""
        data = {
            "email": "",
            "password": "",
            "first_name": "",
            "last_name": "",
            "phone": "",
        }
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        for field in data:
            self.assertIn(field, serializer.errors)
