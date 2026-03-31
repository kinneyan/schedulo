from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from ....views.role import RoleView
from ....models import Workspace, WorkspaceMember, WorkspaceRole, MemberPermissions


class RoleViewTest(TestCase):
    """Test cases for RoleView business logic"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RoleView()

    def _create_drf_request(self, url, data=None, method="get"):
        """Helper method to create properly initialized DRF request"""
        if method == "get":
            request = self.factory.get(url, format="json")
        elif method == "put":
            request = self.factory.put(url, data, format="json")
        elif method == "delete":
            request = self.factory.delete(url, format="json")

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.pk = 1
        request.user = mock_user
        self.view.setup(request)
        return self.view.initialize_request(request)

    # -------------------------
    # GET tests
    # -------------------------

    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.RoleReadSerializer")
    def test_get_role_successful(self, mock_serializer, mock_member_get, mock_role_get):
        """Test successful role retrieval"""
        mock_role = MagicMock()
        mock_role_get.return_value = mock_role

        mock_member_get.return_value = MagicMock()

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.data = {"id": 1, "name": "Manager", "pay_rate": 25.50}
        mock_serializer.return_value = mock_serializer_instance

        request = self._create_drf_request("/roles/1/", method="get")
        response = self.view.get(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"], {"id": 1, "name": "Manager", "pay_rate": 25.50})

    @patch("api.views.role.WorkspaceRole.objects.get")
    def test_get_role_not_found(self, mock_role_get):
        """Test get when role doesn't exist"""
        mock_role_get.side_effect = WorkspaceRole.DoesNotExist

        request = self._create_drf_request("/roles/999/", method="get")
        response = self.view.get(request, role_id=999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["message"], "Workspace role does not exist.")

    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    def test_get_role_not_workspace_member(self, mock_member_get, mock_role_get):
        """Test get when user is not a member of the workspace"""
        mock_role_get.return_value = MagicMock()
        mock_member_get.side_effect = WorkspaceMember.DoesNotExist

        request = self._create_drf_request("/roles/1/", method="get")
        response = self.view.get(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"],
            "Must be a member of the workspace to get a role.",
        )

    # -------------------------
    # PUT tests
    # -------------------------

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_put_role_successful(
        self, mock_permissions_get, mock_member_get, mock_role_get, mock_serializer
    ):
        """Test successful role update"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {"name": "Updated Manager", "pay_rate": 30.00}
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace_role = MagicMock()
        mock_workspace_role.workspace.id = 1
        mock_role_get.return_value = mock_workspace_role

        mock_member_get.return_value = MagicMock()
        mock_permissions_get.return_value = MagicMock()

        request = self._create_drf_request(
            "/roles/1/", {"name": "Updated Manager", "pay_rate": 30.00}, method="put"
        )
        response = self.view.put(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_workspace_role.name, "Updated Manager")
        self.assertEqual(mock_workspace_role.pay_rate, 30.00)
        mock_workspace_role.save.assert_called_once()

    @patch("api.views.role.RoleSerializer")
    def test_put_role_invalid_serializer_data(self, mock_serializer):
        """Test role update with invalid serializer data"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer.return_value = mock_serializer_instance

        request = self._create_drf_request("/roles/1/", {"invalid": "data"}, method="put")
        response = self.view.put(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], 400)
        self.assertEqual(response.data["error"]["message"], "Invalid request data")

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    def test_put_role_not_found(self, mock_role_get, mock_serializer):
        """Test role update when role doesn't exist"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        mock_role_get.side_effect = WorkspaceRole.DoesNotExist

        request = self._create_drf_request("/roles/999/", {"name": "Name"}, method="put")
        response = self.view.put(request, role_id=999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["message"], "Workspace role does not exist.")

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_put_role_insufficient_permissions(
        self, mock_permissions_get, mock_member_get, mock_role_get, mock_serializer
    ):
        """Test role update without manage_workspace_roles permission"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        mock_role_get.return_value = MagicMock()
        mock_member_get.return_value = MagicMock()
        mock_permissions_get.side_effect = MemberPermissions.DoesNotExist

        request = self._create_drf_request("/roles/1/", {"name": "Name"}, method="put")
        response = self.view.put(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"],
            "You do not have permission to modify roles in this workspace.",
        )

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    def test_put_role_not_workspace_member(self, mock_member_get, mock_role_get, mock_serializer):
        """Test role update when user is not a member of the workspace"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer.return_value = mock_serializer_instance

        mock_role_get.return_value = MagicMock()
        mock_member_get.side_effect = WorkspaceMember.DoesNotExist

        request = self._create_drf_request("/roles/1/", {"name": "Name"}, method="put")
        response = self.view.put(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"], "You are not a member of this workspace."
        )

    @patch("api.views.role.RoleSerializer")
    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_put_role_partial_update(
        self, mock_permissions_get, mock_member_get, mock_role_get, mock_serializer
    ):
        """Test role update with only name (no pay_rate)"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {"name": "New Name Only"}
        mock_serializer.return_value = mock_serializer_instance

        mock_workspace_role = MagicMock()
        mock_workspace_role.workspace.id = 1
        mock_workspace_role.pay_rate = 25.00
        mock_role_get.return_value = mock_workspace_role

        mock_member_get.return_value = MagicMock()
        mock_permissions_get.return_value = MagicMock()

        request = self._create_drf_request("/roles/1/", {"name": "New Name Only"}, method="put")
        response = self.view.put(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_workspace_role.name, "New Name Only")
        # pay_rate untouched since it wasn't in validated_data
        mock_workspace_role.save.assert_called_once()

    # -------------------------
    # DELETE tests
    # -------------------------

    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_delete_role_successful(self, mock_permissions_get, mock_member_get, mock_role_get):
        """Test successful role deletion"""
        mock_role = MagicMock()
        mock_role_get.return_value = mock_role
        mock_member_get.return_value = MagicMock()
        mock_permissions_get.return_value = MagicMock()

        request = self._create_drf_request("/roles/1/", method="delete")
        response = self.view.delete(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_role.delete.assert_called_once()

    @patch("api.views.role.WorkspaceRole.objects.get")
    def test_delete_role_not_found(self, mock_role_get):
        """Test role deletion when role doesn't exist"""
        mock_role_get.side_effect = WorkspaceRole.DoesNotExist

        request = self._create_drf_request("/roles/999/", method="delete")
        response = self.view.delete(request, role_id=999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"]["message"],
            "Workspace role does not exist or is not part of this workspace.",
        )

    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    @patch("api.views.role.MemberPermissions.objects.get")
    def test_delete_role_insufficient_permissions(
        self, mock_permissions_get, mock_member_get, mock_role_get
    ):
        """Test role deletion without manage_workspace_roles permission"""
        mock_role_get.return_value = MagicMock()
        mock_member_get.return_value = MagicMock()
        mock_permissions_get.side_effect = MemberPermissions.DoesNotExist

        request = self._create_drf_request("/roles/1/", method="delete")
        response = self.view.delete(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"],
            "You do not have permission to modify roles in this workspace.",
        )

    @patch("api.views.role.WorkspaceRole.objects.get")
    @patch("api.views.role.WorkspaceMember.objects.get")
    def test_delete_role_not_workspace_member(self, mock_member_get, mock_role_get):
        """Test role deletion when user is not a member of the workspace"""
        mock_role_get.return_value = MagicMock()
        mock_member_get.side_effect = WorkspaceMember.DoesNotExist

        request = self._create_drf_request("/roles/1/", method="delete")
        response = self.view.delete(request, role_id=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"]["message"], "You are not a member of this workspace."
        )
