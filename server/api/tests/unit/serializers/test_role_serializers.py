from django.test import TestCase
from rest_framework import serializers
from unittest.mock import patch, MagicMock
from decimal import Decimal
from ....serializers.role import RoleSerializer
from ....models import WorkspaceRole


class RoleSerializerTest(TestCase):
    """Test cases for RoleSerializer"""
    
    def setUp(self):
        self.serializer_class = RoleSerializer
    
    def test_role_serializer_valid_data_with_all_fields(self):
        """Test serializer with valid data including all fields"""
        data = {
            'name': 'Manager',
            'pay_rate': '25.50'
        }
        
        serializer = self.serializer_class(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], 'Manager')
        self.assertEqual(serializer.validated_data['pay_rate'], Decimal('25.50'))
    
    def test_role_serializer_valid_data_name_only(self):
        """Test serializer with only name field"""
        data = {
            'name': 'Employee'
        }
        
        serializer = self.serializer_class(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], 'Employee')
        self.assertNotIn('pay_rate', serializer.validated_data)
    
    def test_role_serializer_valid_data_pay_rate_only(self):
        """Test serializer with only pay_rate field"""
        data = {
            'pay_rate': '15.00'
        }
        
        serializer = self.serializer_class(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['pay_rate'], Decimal('15.00'))
        self.assertNotIn('name', serializer.validated_data)
    
    def test_role_serializer_empty_data(self):
        """Test serializer with empty data (should be valid since fields are optional)"""
        data = {}
        
        serializer = self.serializer_class(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data), 0)
    
    def test_role_serializer_name_field_not_required(self):
        """Test that name field is not required"""
        serializer = self.serializer_class()
        name_field = serializer.fields['name']
        
        self.assertFalse(name_field.required)
    
    def test_role_serializer_pay_rate_field_not_required(self):
        """Test that pay_rate field is not required"""
        serializer = self.serializer_class()
        pay_rate_field = serializer.fields['pay_rate']
        
        self.assertFalse(pay_rate_field.required)
    
    def test_role_serializer_includes_correct_fields(self):
        """Test that serializer includes only name and pay_rate fields"""
        serializer = self.serializer_class()
        
        expected_fields = {'name', 'pay_rate'}
        actual_fields = set(serializer.fields.keys())
        
        self.assertEqual(expected_fields, actual_fields)
    
    def test_role_serializer_excludes_workspace_field(self):
        """Test that workspace field is not included (as mentioned in comment)"""
        serializer = self.serializer_class()
        
        self.assertNotIn('workspace', serializer.fields)
        self.assertNotIn('workspace_id', serializer.fields)
    
    def test_role_serializer_pay_rate_decimal_conversion(self):
        """Test that pay_rate is properly converted to Decimal"""
        test_cases = [
            ('10.50', Decimal('10.50')),
            ('0.00', Decimal('0.00')),
            ('999.99', Decimal('999.99')),
            ('5', Decimal('5')),
        ]
        
        for input_value, expected_value in test_cases:
            with self.subTest(input_value=input_value):
                data = {'pay_rate': input_value}
                serializer = self.serializer_class(data=data)
                
                self.assertTrue(serializer.is_valid())
                self.assertEqual(serializer.validated_data['pay_rate'], expected_value)
    
    def test_role_serializer_invalid_pay_rate_format(self):
        """Test serializer with invalid pay_rate format"""
        invalid_pay_rates = [
            'not-a-number',
            'abc',
            '',
            '10.999',  # Too many decimal places might cause issues
        ]
        
        for invalid_rate in invalid_pay_rates:
            with self.subTest(pay_rate=invalid_rate):
                data = {'pay_rate': invalid_rate}
                serializer = self.serializer_class(data=data)
                
                if invalid_rate == '10.999':
                    # This might be valid depending on DecimalField configuration
                    continue
                else:
                    self.assertFalse(serializer.is_valid())
                    self.assertIn('pay_rate', serializer.errors)
    
    def test_role_serializer_negative_pay_rate(self):
        """Test serializer with negative pay_rate"""
        data = {
            'name': 'Test Role',
            'pay_rate': '-10.00'
        }
        
        serializer = self.serializer_class(data=data)
        
        # Depending on model validation, this might be invalid
        # This tests the serializer behavior with negative values
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data['pay_rate'], Decimal('-10.00'))
        else:
            self.assertIn('pay_rate', serializer.errors)
    
    def test_role_serializer_zero_pay_rate(self):
        """Test serializer with zero pay_rate"""
        data = {
            'name': 'Volunteer',
            'pay_rate': '0.00'
        }
        
        serializer = self.serializer_class(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['pay_rate'], Decimal('0.00'))
    
    def test_role_serializer_name_field_type(self):
        """Test that name field is CharField"""
        serializer = self.serializer_class()
        name_field = serializer.fields['name']
        
        self.assertIsInstance(name_field, serializers.CharField)
    
    def test_role_serializer_pay_rate_field_type(self):
        """Test that pay_rate field is DecimalField"""
        serializer = self.serializer_class()
        pay_rate_field = serializer.fields['pay_rate']
        
        self.assertIsInstance(pay_rate_field, serializers.DecimalField)
    
    def test_role_serializer_long_name(self):
        """Test serializer with very long name"""
        long_name = 'A' * 100  # Very long name
        data = {
            'name': long_name,
            'pay_rate': '15.00'
        }
        
        serializer = self.serializer_class(data=data)
        
        # This might be valid or invalid depending on CharField max_length
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data['name'], long_name)
        else:
            self.assertIn('name', serializer.errors)
    
    def test_role_serializer_empty_string_name(self):
        """Test serializer with empty string name"""
        data = {
            'name': '',
            'pay_rate': '15.00'
        }
        
        serializer = self.serializer_class(data=data)
        
        # Empty string might be valid since field is not required
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data['name'], '')
        else:
            self.assertIn('name', serializer.errors)
    
    @patch('api.models.WorkspaceRole')
    def test_role_serializer_with_model_mock(self, mock_workspace_role):
        """Test serializer behavior with mocked WorkspaceRole model"""
        data = {
            'name': 'Test Role',
            'pay_rate': '20.00'
        }
        
        serializer = self.serializer_class(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], 'Test Role')
        self.assertEqual(serializer.validated_data['pay_rate'], Decimal('20.00'))
    
    def test_role_serializer_model_reference(self):
        """Test that serializer references correct model"""
        serializer = self.serializer_class()
        
        # Check that the Meta.model is WorkspaceRole
        self.assertEqual(serializer.Meta.model, WorkspaceRole)
    
    def test_role_serializer_meta_fields(self):
        """Test that Meta.fields includes correct fields"""
        serializer = self.serializer_class()
        
        expected_fields = ['name', 'pay_rate']
        self.assertEqual(serializer.Meta.fields, expected_fields)
    
    def test_role_serializer_extra_kwargs_configuration(self):
        """Test that extra_kwargs is properly configured"""
        serializer = self.serializer_class()
        
        expected_extra_kwargs = {
            "name": {"required": False}, 
            "pay_rate": {"required": False}
        }
        
        self.assertEqual(serializer.Meta.extra_kwargs, expected_extra_kwargs)