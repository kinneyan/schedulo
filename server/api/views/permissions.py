from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import MemberPermissions, WorkspaceMember, Workspace


class PermissionsView(APIView):
    """API view for retrieving the authenticated user's permissions in a workspace."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Return the authenticated user's permission flags for a given workspace.

        :param request: Authenticated HTTP request containing workspace_id in the body.
        :type request: rest_framework.request.Request
        :return: Permission flags object, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            permissions = MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
                member=WorkspaceMember.objects.get(
                    user=request.user, workspace=request.data["workspace_id"]
                ),
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "Could not find permissions for user in provided workspace."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        response["permissions"] = {
            "is_owner": permissions.is_owner,
            "manage_workspace_members": permissions.manage_workspace_members,
            "manage_workspace_roles": permissions.manage_workspace_roles,
            "manage_schedules": permissions.manage_schedules,
            "manage_time_off": permissions.manage_time_off,
        }

        return Response(response, status=status.HTTP_200_OK)
