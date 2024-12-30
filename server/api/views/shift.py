from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime

from ..serializers import ShiftSerializer
from ..models import Workspace, WorkspaceMember, User, MemberPermissions, WorkspaceRole, MemberRole, Shift

class CreateShift(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self,request):
        response = {"error": {}}

        '''
        workspace_id; the workspace the shift is being made for
        member_id; (optional) member that the shift is being assiged to
        role_id; workspace role that this shift is part of
        start_time
        end_time
        '''

        serializer = ShiftSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data, start and end time are required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify body contains required fields
        if "role_id" not in request.data:
            response["error"]["message"] = "Role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user is part of workspace and has perms to manage schedules
        try:
            creator_member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            creator_permissions = MemberPermissions.objects.get(member=creator_member, MANAGE_SCHEDULES=True)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permissions to manage schedules in this workspace"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        # Verify role exists and is part of workspace
        try:
            role = WorkspaceRole.objects.get(pk=request.data["role_id"], workspace=workspace)
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Workspace role does not exist or is not part of workspace"
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Verify member is valid if present
        if "member_id" in request.data:
            try:
                member = WorkspaceMember.objects.get(pk=request.data["member_id"], workspace=workspace)
            except WorkspaceMember.DoesNotExist:
                response["error"]["message"] = "Member does not exist or is not part of workspace"
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # verify dates are valid
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']

        if start_time > end_time:
            response["error"]["message"] = "Start time cannot be after end time"
            return Response(response, status=status.HTTP_400_BAD_REQUEST) # idk if this is the right status code but wtvr
        
        # could check if start time is before current time if we want to prevent creating shifts in the past, but i think we should allow that since a workplace might want to do that for recordkeeping or smth
        shift = Shift.objects.create(
            workspace = workspace,
            start_time = start_time,
            end_time = end_time,
            created_by = creator_member,
            role = role,
            open = True,
        )

        # Add member to shift if present
        if "member_id" in request.data:          
            shift.member = member
            shift.open = False
            shift.save()

        return Response(response, status=status.HTTP_201_CREATED)
            
        
            
        
        
        
        
        
