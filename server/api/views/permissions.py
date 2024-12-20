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
                    user=request.user, 
                    workspace=request.data["workspace_id"]
                    )
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "Could not find permissions for user in provided workspace."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        response["permissions"] = {
            "is_owner": permissions.IS_OWNER,
            "manage_workspace_members": permissions.MANAGE_WORKSPACE_MEMBERS,
            "manage_workspace_roles": permissions.MANAGE_WORKSPACE_ROLES,
            "manage_schedules": permissions.MANAGE_SCHEDULES,
            "manage_time_off": permissions.MANAGE_TIME_OFF
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
            workspace_member = WorkspaceMember.objects.get(user=request.user, workspace=request.data["workspace_id"])
            permissions = MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
                member=workspace_member,
                MANAGE_WORKSPACE_MEMBERS=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permission to manage permissions for this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        
        try:
            member = WorkspaceMember.objects.get(id=request.data["member_id"])

            # Verify user belongs to correct workspace
            if member.workspace.id != int(request.data["workspace_id"]):
                response["error"]["message"] = "Member does not belong to provided workspace."
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            # Check if permissions already exist
            permissions = MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
                member=member
            )

        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Could not find member with provided ID."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        except MemberPermissions.DoesNotExist:           
            # Create permissions if they do not exist
            permissions = MemberPermissions.objects.create(
                workspace=Workspace.objects.get(id=request.data["workspace_id"]),
                member=member
            )
        
        # Check if user is owner, cannot update owner permissions as they are fixed (all)
        if permissions.IS_OWNER:
            response["error"]["message"] = "Cannot update permissions for workspace owner."
            return Response(response, status=status.HTTP_409_CONFLICT)

        # Check if user is trying to update owner permissions
        if "is_owner" in request.data:
            response["error"]["message"] = "Cannot update owner permission."
            return Response(response, status=status.HTTP_409_CONFLICT)

        # Update permissions
        if "manage_workspace_members" in request.data:
            permissions.MANAGE_WORKSPACE_MEMBERS = request.data["manage_workspace_members"]

        if "manage_workspace_roles" in request.data:
            permissions.MANAGE_WORKSPACE_ROLES = request.data["manage_workspace_roles"]

        if "manage_schedules" in request.data:
            permissions.MANAGE_SCHEDULES = request.data["manage_schedules"]
        
        if "manage_time_off" in request.data:
            permissions.MANAGE_TIME_OFF = request.data["manage_time_off"]
        
        # Save permissions to db
        permissions.save()

        return Response(response, status=status.HTTP_200_OK)
