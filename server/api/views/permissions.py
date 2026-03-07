from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import MemberPermissions, WorkspaceMember, Workspace


class GetPermissions(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
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


class UpdatePermissions(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        response = {"error": {}}

        # Verify body contains required fields
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if "member_id" not in request.data:
            response["error"]["message"] = "Member ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify user has required permissions
        try:
            workspace_member = WorkspaceMember.objects.get(
                user=request.user, workspace=request.data["workspace_id"]
            )
            permissions = MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
                member=workspace_member,
                manage_workspace_members=True,
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission to manage permissions for this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        try:
            member = WorkspaceMember.objects.get(id=request.data["member_id"])

            # Verify user belongs to correct workspace
            if member.workspace.id != int(request.data["workspace_id"]):
                response["error"][
                    "message"
                ] = "Member does not belong to provided workspace."
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            # Check if permissions already exist
            permissions = MemberPermissions.objects.get(
                workspace=request.data["workspace_id"], member=member
            )

        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Could not find member with provided ID."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except MemberPermissions.DoesNotExist:
            # Create permissions if they do not exist
            permissions = MemberPermissions.objects.create(
                workspace=Workspace.objects.get(id=request.data["workspace_id"]),
                member=member,
            )

        # Check if user is owner, cannot update owner permissions as they are fixed (all)
        if permissions.is_owner:
            response["error"][
                "message"
            ] = "Cannot update permissions for workspace owner."
            return Response(response, status=status.HTTP_409_CONFLICT)

        # Check if user is trying to update owner permissions
        if "is_owner" in request.data:
            response["error"]["message"] = "Cannot update owner permission."
            return Response(response, status=status.HTTP_409_CONFLICT)

        # Update permissions
        if "manage_workspace_members" in request.data:
            permissions.manage_workspace_members = request.data[
                "manage_workspace_members"
            ]

        if "manage_workspace_roles" in request.data:
            permissions.manage_workspace_roles = request.data["manage_workspace_roles"]

        if "manage_schedules" in request.data:
            permissions.manage_schedules = request.data["manage_schedules"]

        if "manage_time_off" in request.data:
            permissions.manage_time_off = request.data["manage_time_off"]

        # Save permissions to db
        permissions.save()

        return Response(response, status=status.HTTP_200_OK)
