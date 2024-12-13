from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import Workspace, WorkspaceMember


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