from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import RoleSerializer
from ..models import Workspace, WorkspaceMember, User, MemberPermissions, WorkspaceRole, MemberRole

class CreateRole(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        response = {"error": {}}

        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify body contains required fields
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify workspace exsists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exsist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=request.data["workspace_id"])
            permissions = MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
                member=member,
                MANAGE_WORKSPACE_ROLES=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"]["message"] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        workspace_role = WorkspaceRole.objects.create(workspace=workspace)

        if 'name' in serializer.validated_data:
            workspace_role.name = serializer.validated_data['name']
        if 'pay_rate' in serializer.validated_data:
            workspace_role.pay_rate = serializer.validated_data['pay_rate']

        workspace_role.save()

        return Response(response, status=status.HTTP_201_CREATED)
    
class GetWorkspaceRoles(APIView): # returns a list of all roles in a workspace, reponse[i][0] contains the pk of the role at that index, and response[i][1] contains the name
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {"error": {}}

        # Verify body contains required fields
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exsists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exsist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
  
        roles = WorkspaceRole.objects.filter().values_list("id", "name")

        response['roles'] = list(roles)

        return Response(response, status=status.HTTP_200_OK)
