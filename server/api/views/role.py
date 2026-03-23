from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import RoleSerializer, RoleReadSerializer
from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
)


class RoleView(APIView):
    """API view for workspace role."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, role_id):
        """Get a given WorkspaceRole, must be a member of the workspace the role belongs to.

        :param request: Authenticated HTTP request with role_id in url params
        """

        response = {"error": {}}

        # Verify role exists
        try:
            role = WorkspaceRole.objects.get(pk=role_id)
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Workspace role does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # verify user is member of workspace with role
        try:
            _ = WorkspaceMember.objects.get(user=request.user, workspace=role.workspace)
        except WorkspaceMember.DoesNotExist:
            response["error"][
                "message"
            ] = "Must be a member of the workspace to get a role."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        data = RoleReadSerializer(role).data
        response["result"] = data

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, role_id):
        """Update name and/or pay_rate for an existing WorkspaceRole.

        Requires manage_workspace_roles permission. Accepted body fields:
        name (optional), pay_rate (optional).

        :param request: Authenticated HTTP request with workspace_role_id and
            optional update fields in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response, or an error response describing the failure.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify role exists
        try:
            workspace_role = WorkspaceRole.objects.get(pk=role_id)
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Workspace role does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        workspace = workspace_role.workspace

        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            MemberPermissions.objects.get(
                workspace=workspace, member=member, manage_workspace_roles=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission to modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # modify role
        if "name" in serializer.validated_data:
            workspace_role.name = serializer.validated_data["name"]
        if "pay_rate" in serializer.validated_data:
            workspace_role.pay_rate = serializer.validated_data["pay_rate"]

        workspace_role.save()

        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, role_id):
        """Delete a WorkspaceRole by ID.

        :param request: Authenticated HTTP request containing workspace_role_id
            in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on deletion, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Verify role exists
        try:
            role = WorkspaceRole.objects.get(id=role_id)
        except WorkspaceRole.DoesNotExist:
            response["error"][
                "message"
            ] = "Workspace role does not exist or is not part of this workspace."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Get role's workspace
        try:
            workspace = Workspace.objects.get(id=role.workspace.id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            MemberPermissions.objects.get(
                workspace=workspace, member=member, manage_workspace_roles=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission to modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # delete role
        role.delete()
        return Response(response, status=status.HTTP_200_OK)
