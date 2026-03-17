from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import RoleSerializer
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
        # TODO
        return None

    def put(self, request):
        """Update name and/or pay_rate for an existing WorkspaceRole.

        Requires manage_workspace_roles permission. Accepted body fields:
        workspace_role_id (required), name (optional), pay_rate (optional).

        :param request: Authenticated HTTP request with workspace_role_id and
            optional update fields in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response, or an error response describing the failure.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Workspace role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify role exists
        try:
            workspace_role = WorkspaceRole.objects.get(
                pk=request.data["workspace_role_id"]
            )
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Workspace role does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify workspace exists; this shouldnt ever fail but have to get the workspace
        try:
            workspace = Workspace.objects.get(pk=workspace_role.workspace.id)
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
            ] = "You do not have permission modify roles in this workspace."
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

    def delete(self, request):
        """Delete a WorkspaceRole by ID.

        :param request: Authenticated HTTP request containing workspace_role_id
            in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on deletion, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Workspace role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify role exists
        try:
            role = WorkspaceRole.objects.get(id=request.data["workspace_role_id"])
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
            ] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # delete role
        role = WorkspaceRole.objects.get(id=request.data["workspace_role_id"]).delete()
        return Response(response, status=status.HTTP_200_OK)
