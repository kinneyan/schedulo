from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from ..models import Workspace, WorkspaceMember


class GetUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = {"error": {}}

        response["email"] = request.user.email
        response["phone"] = request.user.phone
        response["first_name"] = request.user.first_name
        response["last_name"] = request.user.last_name

        # get list of workspaces user is in
        members = WorkspaceMember.objects.filter(user=request.user).values_list(
            "workspace"
        )
        results = Workspace.objects.filter(pk__in=members)

        workspace_list = [
            {
                "id": workspace.id,
                "created_by": workspace.created_by.id,
                "owner": workspace.owner.id,
                "name": workspace.name,
            }
            for workspace in results
        ]

        response["workspaces"] = workspace_list

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request):
        """
        email
        phone
        first_name
        last_name
        last_name
        password
        current_password
        """
        response = {"error": {}}

        if "email" in request.data:
            try:
                validate_email(request.data["email"])
                request.user.email = request.data["email"]
                request.user.save()
            except ValidationError:
                response["error"]["email"] = "Invalid email format"
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if "password" in request.data:
            if "current_password" not in request.data:
                response["error"][
                    "message"
                ] = "Current password required when changing password."
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            auth = authenticate(
                email=request.user, password=request.data["current_password"]
            )
            if auth == request.user:
                request.user.set_password(request.data["password"])
                request.user.save()
            else:
                response["error"]["message"] = "Current password is incorrect."
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if "phone" in request.data:
            request.user.phone = request.data["phone"]
            request.user.save()

        if "first_name" in request.data:
            request.user.first_name = request.data["first_name"]
            request.user.save()

        if "last_name" in request.data:
            request.user.last_name = request.data["last_name"]
            request.user.save()

        return Response(response, status=status.HTTP_200_OK)
