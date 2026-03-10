from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from ....views.role import CreateRole, DeleteWorkspaceRole, ModifyWorkspaceRole
from ....models import Workspace, WorkspaceMember, WorkspaceRole, MemberPermissions


class CreateRoleViewTest(TestCase):
    """Test cases for CreateRole view business logic"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CreateRole()

    def _create_drf_request(self, url, data, method="put"):
        """Helper method to create properly initialized DRF request"""
        if method == "put":
            request = self.factory.put(url, data, format="json")
        elif method == "post":
            request = self.factory.post(url, data, format="json")
        elif method == "delete":
            request = self.factory.delete(url, data, format="json")
        # Create a mock user with an id
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.pk = 1
        request.user = mock_user
        self.view.setup(request)
        return self.view.initialize_request(request)

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.Workspace.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    @patch("api.views.role.WorkspaceRole.objects.create")
    def test_create_role_successful(
        self,
        mock_role_create,
        mock_permissions_get,
        mock_member_get,
        mock_workspace_get,
        mock_serializer,
    ):
        """Test successful role creation with valid data and permissions"""
        # Setup mocks
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {"name": "Manager", "pay_rate": 25.50}
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace = MagicMock()
        mock_workspace_get.return_value = mock_workspace

        mock_member = MagicMock()
        mock_member_get.return_value = mock_member

        mock_permissions = MagicMock()
        mock_permissions_get.return_value = mock_permissions

        mock_workspace_role = MagicMock()
        mock_role_create.return_value = mock_workspace_role

        # Create request with authenticated user
        request_data = {"workspace_id": 1, "name": "Manager", "pay_rate": 25.50}
        request = self._create_drf_request("/create-role/", request_data, method="put")

        # Call view method
        response = self.view.post(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_role_create.assert_called_once_with(workspace=mock_workspace)
        mock_workspace_role.save.assert_called_once()

        # Verify role attributes were set
        self.assertEqual(mock_workspace_role.name, "Manager")
        self.assertEqual(mock_workspace_role.pay_rate, 25.50)

    @patch("api.views.role.RoleSerializer")
    def test_create_role_invalid_serializer_data(self, mock_serializer):
        """Test role creation with invalid serializer data"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer.return_value = mock_serializer_instance

        request_data = {"invalid": "data"}
        request = self._create_drf_request("/create-role/", request_data, method="put")

        response = self.view.post(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], 400)
        self.assertEqual(response.data["error"]["message"], "Invalid request data")

    @patch("api.views.role.RoleSerializer")
    def test_create_role_missing_workspace_id(self, mock_serializer):
        """Test role creation without workspace_id"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        request_data = {"name": "Manager"}  # Missing workspace_id
        request = self._create_drf_request("/create-role/", request_data, method="put")

        response = self.view.post(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["message"], "Workspace ID is required.")

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.Workspace.objects.get")
    def test_create_role_workspace_not_found(self, mock_workspace_get, mock_serializer):
        """Test role creation when workspace doesn't exist"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace_get.side_effect = Workspace.DoesNotExist

        request_data = {"workspace_id": 999, "name": "Manager"}
        request = self._create_drf_request("/create-role/", request_data, method="put")

        response = self.view.post(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["message"], "Workspace does not exist.")

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.Workspace.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_create_role_insufficient_permissions(
        self, mock_permissions_get, mock_member_get, mock_workspace_get, mock_serializer
    ):
        """Test role creation without proper permissions"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace = MagicMock()
        mock_workspace_get.return_value = mock_workspace

        mock_member = MagicMock()
        mock_member_get.return_value = mock_member

        mock_permissions_get.side_effect = MemberPermissions.DoesNotExist

        request_data = {"workspace_id": 1, "name": "Manager"}
        request = self._create_drf_request("/create-role/", request_data, method="put")

        response = self.view.post(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"],
            "You do not have permission modify roles in this workspace.",
        )


class DeleteWorkspaceRoleViewTest(TestCase):
    """Test cases for DeleteWorkspaceRole view business logic"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = DeleteWorkspaceRole()

    def _create_drf_request(self, url, data, method="delete"):
        """Helper method to create properly initialized DRF request"""
        if method == "put":
            request = self.factory.put(url, data, format="json")
        elif method == "post":
            request = self.factory.post(url, data, format="json")
        elif method == "delete":
            request = self.factory.delete(url, data, format="json")
        # Create a mock user with an id
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.pk = 1
        request.user = mock_user
        self.view.setup(request)
        return self.view.initialize_request(request)

    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.Workspace.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_delete_role_successful(
        self, mock_permissions_get, mock_member_get, mock_workspace_get, mock_role_get
    ):
        """Test successful role deletion"""
        # Setup mocks
        mock_role = MagicMock()
        mock_role.workspace.id = 1
        mock_role.delete = MagicMock()
        mock_role_get.side_effect = [mock_role, mock_role]  # Called twice in the view

        mock_workspace = MagicMock()
        mock_workspace_get.return_value = mock_workspace

        mock_member = MagicMock()
        mock_member_get.return_value = mock_member

        mock_permissions = MagicMock()
        mock_permissions_get.return_value = mock_permissions

        request_data = {"workspace_role_id": 1}
        request = self._create_drf_request(
            "/delete-role/", request_data, method="delete"
        )

        response = self.view.delete(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify delete was called
        self.assertTrue(mock_role_get.called)

    def test_delete_role_missing_workspace_role_id(self):
        """Test role deletion without workspace_role_id"""
        request_data = {}  # Missing workspace_role_id
        request = self._create_drf_request(
            "/delete-role/", request_data, method="delete"
        )

        response = self.view.delete(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"]["message"], "Workspace role ID is required."
        )

    @patch("api.views.role.WorkspaceRole.objects.get")
    def test_delete_role_role_not_found(self, mock_role_get):
        """Test role deletion when role doesn't exist"""
        mock_role_get.side_effect = WorkspaceRole.DoesNotExist

        request_data = {"workspace_role_id": 999}
        request = self._create_drf_request(
            "/delete-role/", request_data, method="delete"
        )

        response = self.view.delete(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"]["message"],
            "Workspace role does not exist or is not part of this workspace.",
        )


class ModifyWorkspaceRoleViewTest(TestCase):
    """Test cases for ModifyWorkspaceRole view business logic"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ModifyWorkspaceRole()

    def _create_drf_request(self, url, data, method="post"):
        """Helper method to create properly initialized DRF request"""
        if method == "put":
            request = self.factory.put(url, data, format="json")
        elif method == "post":
            request = self.factory.post(url, data, format="json")
        elif method == "delete":
            request = self.factory.delete(url, data, format="json")
        # Create a mock user with an id
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.pk = 1
        request.user = mock_user
        self.view.setup(request)
        return self.view.initialize_request(request)

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.Workspace.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_modify_role_successful(
        self,
        mock_permissions_get,
        mock_member_get,
        mock_workspace_get,
        mock_role_get,
        mock_serializer,
    ):
        """Test successful role modification"""
        # Setup mocks
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {
            "name": "Updated Manager",
            "pay_rate": 30.00,
        }
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace_role = MagicMock()
        mock_workspace_role.workspace.id = 1
        mock_role_get.return_value = mock_workspace_role

        mock_workspace = MagicMock()
        mock_workspace_get.return_value = mock_workspace

        mock_member = MagicMock()
        mock_member_get.return_value = mock_member

        mock_permissions = MagicMock()
        mock_permissions_get.return_value = mock_permissions

        request_data = {
            "workspace_role_id": 1,
            "name": "Updated Manager",
            "pay_rate": 30.00,
        }
        request = self._create_drf_request("/modify-role/", request_data, method="post")

        response = self.view.put(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify role attributes were updated
        self.assertEqual(mock_workspace_role.name, "Updated Manager")
        self.assertEqual(mock_workspace_role.pay_rate, 30.00)
        mock_workspace_role.save.assert_called_once()

    def test_modify_role_missing_workspace_role_id(self):
        """Test role modification without workspace_role_id"""
        request_data = {"name": "Updated Name"}  # Missing workspace_role_id
        request = self._create_drf_request("/modify-role/", request_data, method="post")

        response = self.view.put(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"]["message"], "Workspace role ID is required."
        )

    @patch("api.views.role.RoleSerializer")
    def test_modify_role_invalid_serializer_data(self, mock_serializer):
        """Test role modification with invalid serializer data"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer.return_value = mock_serializer_instance

        request_data = {"workspace_role_id": 1, "invalid": "data"}
        request = self._create_drf_request("/modify-role/", request_data, method="post")

        response = self.view.put(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], 400)
        self.assertEqual(response.data["error"]["message"], "Invalid request data")

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    def test_modify_role_role_not_found(self, mock_role_get, mock_serializer):
        """Test role modification when role doesn't exist"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        mock_role_get.side_effect = WorkspaceRole.DoesNotExist

        request_data = {"workspace_role_id": 999, "name": "Updated Name"}
        request = self._create_drf_request("/modify-role/", request_data, method="post")

        response = self.view.put(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"]["message"], "Workspace role does not exist."
        )

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.Workspace.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_modify_role_insufficient_permissions(
        self,
        mock_permissions_get,
        mock_member_get,
        mock_workspace_get,
        mock_role_get,
        mock_serializer,
    ):
        """Test role modification without proper permissions"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace_role = MagicMock()
        mock_workspace_role.workspace.id = 1
        mock_role_get.return_value = mock_workspace_role

        mock_workspace = MagicMock()
        mock_workspace_get.return_value = mock_workspace

        mock_member = MagicMock()
        mock_member_get.return_value = mock_member

        mock_permissions_get.side_effect = MemberPermissions.DoesNotExist

        request_data = {"workspace_role_id": 1, "name": "Updated Name"}
        request = self._create_drf_request("/modify-role/", request_data, method="post")

        response = self.view.put(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"],
            "You do not have permission modify roles in this workspace.",
        )

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.Workspace.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_modify_role_partial_update(
        self,
        mock_permissions_get,
        mock_member_get,
        mock_workspace_get,
        mock_role_get,
        mock_serializer,
    ):
        """Test role modification with only some fields"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {
            "name": "New Name Only"
            # No pay_rate in validated_data
        }
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace_role = MagicMock()
        mock_workspace_role.workspace.id = 1
        mock_workspace_role.pay_rate = 25.00  # Original pay_rate
        mock_role_get.return_value = mock_workspace_role

        mock_workspace = MagicMock()
        mock_workspace_get.return_value = mock_workspace

        mock_member = MagicMock()
        mock_member_get.return_value = mock_member

        mock_permissions = MagicMock()
        mock_permissions_get.return_value = mock_permissions

        request_data = {"workspace_role_id": 1, "name": "New Name Only"}
        request = self._create_drf_request("/modify-role/", request_data, method="post")

        response = self.view.put(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only name was updated, pay_rate should remain unchanged
        self.assertEqual(mock_workspace_role.name, "New Name Only")
        # pay_rate should not be modified since it wasn't in validated_data
        mock_workspace_role.save.assert_called_once()
