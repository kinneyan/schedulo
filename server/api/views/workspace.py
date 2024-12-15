from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import CreateWorkspaceSerializer
from ..models import Workspace, WorkspaceMember, User, MemberPermissions


class CreateWorkspace(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {"error": {}}

        # get name from request using serializer
        serializer = CreateWorkspaceSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # create new workspace
        workspace = Workspace.objects.create(
            created_by_id = request.user,
            owner_id = request.user
        )

        # set name if present
        if not (serializer.data.get('name',None) == None):
            name = serializer.validated_data['name']
            workspace.name = name
            workspace.save()

        # add creator of workspace as owner of the new workspace
        workspace_member = WorkspaceMember.objects.create(
            workspace_id = workspace,
            user_id = request.user,
            added_by_id = request.user
        )

        return Response(response, status=status.HTTP_201_CREATED)
    
class AddWorkspaceMember(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        '''
        body:
            added_user_id
            workspace_id
            pay_rate (optional)
            workspace_role_id (optional) # not yet implemented
        '''
        response = {"error": {}}

        # Verify user is permitted to add members to workspace
        try:
            workspace_member = WorkspaceMember.objects.get(user_id=request.user, workspace_id=request.data['workspace_id'])
            MemberPermissions.objects.get(member_id=workspace_member, workspace_id=request.data['workspace_id'], MANAGE_WORKSPACE_MEMBERS=True)
        except MemberPermissions.DoesNotExist:
            response["error"] = "You do not have permission to add members to this workspace"
            return Response(response, status=status.HTTP_403_FORBIDDEN)


        if not (WorkspaceMember.objects.filter(user_id=User.objects.get(pk=request.data['added_user_id']), workspace_id=Workspace.objects.get(pk=request.data['workspace_id'])).exists()): # check if user is already member of workspace
            workspace_member = WorkspaceMember.objects.create(
                workspace_id = Workspace.objects.get(pk=request.data['workspace_id']),
                user_id = User.objects.get(pk=request.data['added_user_id']),
                added_by_id = request.user
            )

            if "pay_rate" in request.data:
                workspace_member.pay_rate = request.data['pay_rate']
                workspace_member.save()

            # TODO: Add role to new member once roles implemented
            
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response["error"] = "User is already member of this workspace"
            return Response(response, status=status.HTTP_409_CONFLICT)
        
        