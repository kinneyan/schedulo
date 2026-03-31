from django.test import TestCase
from decimal import Decimal
from ....serializers.role import RoleSerializer


class RoleSerializerTest(TestCase):
    """Test cases for RoleSerializer"""

    def setUp(self):
        self.serializer_class = RoleSerializer

    def test_valid_data_with_all_fields(self):
        data = {"name": "Manager", "pay_rate": "25.50"}
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Manager")
        self.assertEqual(serializer.validated_data["pay_rate"], Decimal("25.50"))

    def test_name_only(self):
        """Name alone is valid; pay_rate is optional"""
        serializer = self.serializer_class(data={"name": "Employee"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Employee")
        self.assertNotIn("pay_rate", serializer.validated_data)

    def test_pay_rate_only(self):
        """pay_rate alone is valid; name is optional"""
        serializer = self.serializer_class(data={"pay_rate": "15.00"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["pay_rate"], Decimal("15.00"))
        self.assertNotIn("name", serializer.validated_data)

    def test_empty_data(self):
        """Both fields optional — empty body is valid"""
        serializer = self.serializer_class(data={})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data), 0)

    def test_pay_rate_decimal_conversion(self):
        """pay_rate string inputs are converted to Decimal correctly"""
        cases = [
            ("10.50", Decimal("10.50")),
            ("0.00", Decimal("0.00")),
            ("999.99", Decimal("999.99")),
            ("5", Decimal("5")),
        ]
        for input_value, expected in cases:
            with self.subTest(input_value=input_value):
                serializer = self.serializer_class(data={"pay_rate": input_value})
                self.assertTrue(serializer.is_valid())
                self.assertEqual(serializer.validated_data["pay_rate"], expected)

    def test_zero_pay_rate(self):
        serializer = self.serializer_class(data={"name": "Volunteer", "pay_rate": "0.00"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["pay_rate"], Decimal("0.00"))

    def test_non_numeric_pay_rate_invalid(self):
        for invalid in ["not-a-number", "abc"]:
            with self.subTest(pay_rate=invalid):
                serializer = self.serializer_class(data={"pay_rate": invalid})
                self.assertFalse(serializer.is_valid())
                self.assertIn("pay_rate", serializer.errors)
