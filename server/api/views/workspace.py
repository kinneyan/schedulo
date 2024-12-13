from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import Workspace, WorkspaceMember, User


class CreateWorkspace(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {"error": {}}

        # TODO: get workspace name from request with serializer once name implemented

        workspace = Workspace.objects.create(
            created_by_id = request.user,
            owner_id = request.user
        )

        workspace_member = WorkspaceMember.objects.create(
            workspace_id = workspace,
            user_id = request.user,
            added_by_id = request.user
        )

        return Response(response, status=status.HTTP_200_OK)
    
class AddWorkspaceMember(APIView):
    '''
    body:
        added_user_id
        workspace_id
        pay_rate (optional)
        workspace_role_id (optional) # not yet implemented
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # TODO: Authenticate that user is allowed to add another user to workspace

        response = {"error": {}}

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
            
            return Response(response, status=status.HTTP_200_OK)
        else:
            response["error"] = "User is already member of this workspace"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        