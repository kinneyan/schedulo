from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.response import Response
from unittest.mock import patch, MagicMock
from ....views.auth import Login, Register
from ....models import User


class LoginViewTest(TestCase):
    """Test cases for Login view business logic"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = Login()
        self.view.request = None  # Will be set in each test
    
    @patch('api.views.auth.LoginUserSerializer')
    @patch('api.views.auth.authenticate')
    @patch('api.views.auth.CustomTokenObtainPairSerializer')
    def test_login_successful_with_valid_credentials(self, mock_token_serializer, mock_authenticate, mock_login_serializer):
        """Test successful login with valid credentials"""
        # Setup mocks
        mock_login_instance = MagicMock()
        mock_login_instance.is_valid.return_value = True
        mock_login_instance.validated_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        mock_login_serializer.return_value = mock_login_instance
        
        mock_user = MagicMock()
        mock_authenticate.return_value = mock_user
        
        mock_token_instance = MagicMock()
        mock_token_instance.is_valid.return_value = True
        mock_token_instance.validated_data = {
            'access': 'access_token_123',
            'refresh': 'refresh_token_456'
        }
        mock_token_serializer.return_value = mock_token_instance
        
        # Create request
        request_data = {'email': 'test@example.com', 'password': 'password123'}
        request = self.factory.post('/login/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['access'], 'access_token_123')
        self.assertEqual(response.data['refresh'], 'refresh_token_456')
        
        # Verify mocks were called correctly
        mock_login_serializer.assert_called_once_with(data=request_data)
        mock_authenticate.assert_called_once_with(email='test@example.com', password='password123')
        mock_token_serializer.assert_called_once_with(data=request_data)
    
    @patch('api.views.auth.LoginUserSerializer')
    def test_login_invalid_request_data(self, mock_login_serializer):
        """Test login with invalid request data"""
        # Setup mock
        mock_login_instance = MagicMock()
        mock_login_instance.is_valid.return_value = False
        mock_login_serializer.return_value = mock_login_instance
        
        # Create request
        request_data = {'email': 'test@example.com'}  # Missing password
        request = self.factory.post('/login/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error']['code'], 400)
        self.assertEqual(response.data['error']['message'], 'Invalid request data')
    
    @patch('api.views.auth.LoginUserSerializer')
    @patch('api.views.auth.authenticate')
    def test_login_user_does_not_exist(self, mock_authenticate, mock_login_serializer):
        """Test login when user does not exist"""
        # Setup mocks
        mock_login_instance = MagicMock()
        mock_login_instance.is_valid.return_value = True
        mock_login_instance.validated_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        mock_login_serializer.return_value = mock_login_instance
        
        mock_authenticate.return_value = None  # User not found
        
        # Create request
        request_data = {'email': 'nonexistent@example.com', 'password': 'password123'}
        request = self.factory.post('/login/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error']['code'], 401)
        self.assertEqual(response.data['error']['message'], 'Incorrect email or password')
    
    @patch('api.views.auth.LoginUserSerializer')
    @patch('api.views.auth.authenticate')
    @patch('api.views.auth.CustomTokenObtainPairSerializer')
    def test_login_token_serializer_invalid(self, mock_token_serializer, mock_authenticate, mock_login_serializer):
        """Test login when token serializer is invalid"""
        # Setup mocks
        mock_login_instance = MagicMock()
        mock_login_instance.is_valid.return_value = True
        mock_login_instance.validated_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        mock_login_serializer.return_value = mock_login_instance
        
        mock_user = MagicMock()
        mock_authenticate.return_value = mock_user
        
        mock_token_instance = MagicMock()
        mock_token_instance.is_valid.return_value = False  # Token serializer fails
        mock_token_serializer.return_value = mock_token_instance
        
        # Create request
        request_data = {'email': 'test@example.com', 'password': 'password123'}
        request = self.factory.post('/login/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error']['code'], 401)
        self.assertEqual(response.data['error']['message'], 'Incorrect email or password')


class RegisterViewTest(TestCase):
    """Test cases for Register view business logic"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = Register()
        self.view.request = None
    
    @patch('api.views.auth.RegisterUserSerializer')
    @patch('api.views.auth.User.objects.create_user')
    @patch('api.views.auth.CustomTokenObtainPairSerializer')
    def test_register_successful_with_valid_data(self, mock_token_serializer, mock_create_user, mock_register_serializer):
        """Test successful registration with valid data"""
        # Setup mocks
        mock_register_instance = MagicMock()
        mock_register_instance.is_valid.return_value = True
        mock_register_instance.validated_data = {
            'email': 'newuser@example.com',
            'password': 'securepassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890'
        }
        mock_register_serializer.return_value = mock_register_instance
        
        mock_user = MagicMock()
        mock_user.email = 'newuser@example.com'
        mock_create_user.return_value = mock_user
        
        mock_token_instance = MagicMock()
        mock_token_instance.is_valid.return_value = True
        mock_token_instance.validated_data = {
            'access': 'access_token_123',
            'refresh': 'refresh_token_456'
        }
        mock_token_serializer.return_value = mock_token_instance
        
        # Create request
        request_data = {
            'email': 'newuser@example.com',
            'password': 'securepassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890'
        }
        request = self.factory.post('/register/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verify user creation was called correctly
        mock_create_user.assert_called_once_with(
            email='newuser@example.com',
            password='securepassword',
            first_name='John',
            last_name='Doe',
            phone='1234567890'
        )
        mock_user.save.assert_called_once()
    
    @patch('api.views.auth.RegisterUserSerializer')
    def test_register_invalid_request_data(self, mock_register_serializer):
        """Test registration with invalid request data"""
        # Setup mock
        mock_register_instance = MagicMock()
        mock_register_instance.is_valid.return_value = False
        mock_register_instance.errors = {'email': ['This field is required.']}
        mock_register_serializer.return_value = mock_register_instance
        
        # Create request
        request_data = {'password': 'securepassword'}  # Missing required fields
        request = self.factory.post('/register/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error']['code'], 400)
        self.assertEqual(response.data['error']['message'], 'Invalid request data')
    
    @patch('api.views.auth.RegisterUserSerializer')
    def test_register_email_already_exists(self, mock_register_serializer):
        """Test registration when email already exists"""
        # Setup mock
        mock_register_instance = MagicMock()
        mock_register_instance.is_valid.return_value = False
        mock_error = MagicMock()
        mock_error.code = 'unique'
        mock_register_instance.errors = {'email': [mock_error]}
        mock_register_serializer.return_value = mock_register_instance
        
        # Create request
        request_data = {
            'email': 'existing@example.com',
            'password': 'securepassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890'
        }
        request = self.factory.post('/register/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error']['code'], 409)
        self.assertEqual(response.data['error']['message'], 'Account with this email already exists')
    
    @patch('api.views.auth.RegisterUserSerializer')
    @patch('api.views.auth.User.objects.create_user')
    def test_register_internal_server_error(self, mock_create_user, mock_register_serializer):
        """Test registration when unexpected exception occurs"""
        # Setup mocks
        mock_register_instance = MagicMock()
        mock_register_instance.is_valid.return_value = True
        mock_register_instance.validated_data = {
            'email': 'test@example.com',
            'password': 'password',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890'
        }
        mock_register_serializer.return_value = mock_register_instance
        
        # Make create_user raise an exception
        mock_create_user.side_effect = Exception("Database error")
        
        # Create request
        request_data = {
            'email': 'test@example.com',
            'password': 'password',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890'
        }
        request = self.factory.post('/register/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error']['code'], 500)
        self.assertEqual(response.data['error']['message'], 'Internal server error')
    
    @patch('api.views.auth.RegisterUserSerializer')
    @patch('api.views.auth.User.objects.create_user')
    @patch('api.views.auth.CustomTokenObtainPairSerializer')
    def test_register_token_generation_logic(self, mock_token_serializer, mock_create_user, mock_register_serializer):
        """Test that token generation uses correct data"""
        # Setup mocks
        mock_register_instance = MagicMock()
        mock_register_instance.is_valid.return_value = True
        mock_register_instance.validated_data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890'
        }
        mock_register_serializer.return_value = mock_register_instance
        
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'
        mock_create_user.return_value = mock_user
        
        mock_token_instance = MagicMock()
        mock_token_instance.is_valid.return_value = True
        mock_token_instance.validated_data = {
            'access': 'access_token',
            'refresh': 'refresh_token'
        }
        mock_token_serializer.return_value = mock_token_instance
        
        # Create request
        request_data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890'
        }
        request = self.factory.post('/register/', request_data, format='json')
        self.view.request = request
        
        # Call view method
        response = self.view.post(request)
        
        # Verify token serializer was called with correct data
        expected_token_data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        mock_token_serializer.assert_called_once_with(data=expected_token_data)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_register_view_response_structure(self):
        """Test that view response always includes error structure"""
        with patch('api.views.auth.RegisterUserSerializer') as mock_serializer:
            mock_instance = MagicMock()
            mock_instance.is_valid.return_value = False
            mock_instance.errors = {}
            mock_serializer.return_value = mock_instance
            
            request = self.factory.post('/register/', {})
            response = self.view.post(request)
            
            # Response should always have error structure
            self.assertIn('error', response.data)
            self.assertIsInstance(response.data['error'], dict)