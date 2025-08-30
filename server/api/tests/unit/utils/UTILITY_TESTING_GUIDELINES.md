# Utility Function Testing Guidelines

This directory is for testing utility functions and helpers. Currently, no utility files exist in the codebase, but when they are added, follow these guidelines for comprehensive testing.

## Testing Patterns for Future Utilities

### 1. Pure Function Testing
Test functions with no side effects - just verify input/output.

```python
def test_calculate_hours_worked(self):
    """Test pure calculation function"""
    from datetime import datetime
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 17, 0)
    result = calculate_hours_worked(start, end)
    self.assertEqual(result, 8.0)
```

### 2. Time-Dependent Function Testing
Use mocks to control time-based behavior.

```python
@patch('django.utils.timezone.now')
def test_is_business_hours(self, mock_now):
    """Test time-dependent function with mocked time"""
    mock_now.return_value = datetime(2025, 1, 1, 12, 0)
    result = is_business_hours()
    self.assertTrue(result)
```

### 3. Validation Function Testing
Test all validation rules and edge cases comprehensively.

```python
def test_validate_phone_number(self):
    """Test phone validation with comprehensive cases"""
    test_cases = [
        ("1234567890", True),   # Valid
        ("123456789", False),   # Too short
        ("12345678901", False), # Too long  
        ("123456789a", False),  # Contains letter
        ("", False),            # Empty
        (None, False),          # None
    ]
    
    for phone, expected in test_cases:
        with self.subTest(phone=phone):
            result = validate_phone_number(phone)
            self.assertEqual(result, expected)
```

### 4. Database Utility Testing
Mock database calls to test logic without hitting the database.

```python
@patch('api.models.User.objects.filter')
def test_get_user_workspaces(self, mock_filter):
    """Test database utility with mocked queries"""
    mock_user = MagicMock()
    mock_user.workspaces.all.return_value = ["workspace1", "workspace2"]
    mock_filter.return_value.first.return_value = mock_user
    
    result = get_user_workspaces("test@example.com")
    self.assertEqual(len(result), 2)
    mock_filter.assert_called_once_with(email="test@example.com")
```

## Common Utility Patterns for This Project

Based on the existing codebase, these are likely utility patterns that would be useful:

### Error Response Formatter
```python
def test_format_error_response(self):
    """Test error response formatting utility"""
    result = format_error_response(400, "Test message")
    expected = {"error": {"code": 400, "message": "Test message"}}
    self.assertEqual(result, expected)
```

### Permission Checker
```python
@patch('api.models.WorkspaceMember.objects.get')
@patch('api.models.MemberPermissions.objects.get')
def test_check_workspace_role_permissions(self, mock_perms, mock_member):
    """Test permission checking utility"""
    mock_member.return_value = MagicMock()
    mock_perms.return_value = MagicMock()
    
    result = check_workspace_role_permissions(mock_user, workspace_id=1)
    self.assertIsNotNone(result)
```

### Data Cleaner
```python
def test_clean_optional_fields(self):
    """Test data cleaning utility"""
    data = {
        "required_field": "value",
        "optional_field": None,
        "other_optional": "has_value"
    }
    optional_fields = ["optional_field", "other_optional"]
    
    result = clean_optional_fields(data, optional_fields)
    expected = {
        "required_field": "value",
        "other_optional": "has_value"
    }
    self.assertEqual(result, expected)
```

## Testing Best Practices

1. **Test in Isolation**: Mock external dependencies
2. **Fast Execution**: No database/network calls in utility tests  
3. **Comprehensive Coverage**: Test success, failure, and edge cases
4. **Clear Naming**: `test_function_condition_expected_result`
5. **Focused Scope**: One test per specific behavior
6. **Use Mocks Properly**: `@patch` and `MagicMock` for isolation

## File Structure

When adding utility functions, organize tests like:

```
server/api/tests/unit/utils/
├── test_validation_utils.py     # Email, phone, data validation
├── test_permission_utils.py     # Permission checking helpers
├── test_response_utils.py       # Error response formatters
├── test_datetime_utils.py       # Date/time calculation helpers
└── test_data_utils.py          # Data cleaning/transformation
```

## Integration with Existing Tests

Utility functions should complement, not duplicate, the existing integration tests. Focus on:

- **Logic Testing**: Business rules and calculations
- **Validation Testing**: Input sanitization and validation  
- **Formatting Testing**: Response formatting and data transformation
- **Helper Testing**: Common operations used across multiple views