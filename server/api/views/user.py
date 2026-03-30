from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from ..models import Workspace, WorkspaceMember
from ..serializers import UserDetailedReadSerializer, WorkspaceReadSerializer


class GetUser(APIView):
    """API view for retrieving and updating the authenticated user's profile."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the authenticated user's profile and their workspace memberships.

        :param request: Authenticated HTTP request.
        :type request: rest_framework.request.Request
        :return: User profile fields and a list of workspaces the user belongs to.
        :rtype: rest_framework.response.Response


        result: {
            user: {
                id: user id
                first_name: first name
                last_name: last name
                phone: phone #
                email: email
            }
            workspaces: [
                {
                    id: workspace id
                    name: workspace name
                    owner: {
                        first_name: owner first name
                        last_name: owner last name
                    },
                    ...
                }
            ]
        }
        """
        response = {"error": {}, "result": {}}

        response["result"]["user"] = UserDetailedReadSerializer(request.user).data

        # get list of workspaces user is in
        members = WorkspaceMember.objects.filter(user=request.user).values_list("workspace")
        results = Workspace.objects.filter(pk__in=members).select_related("owner")

        workspace_list = [
            {
                "id": workspace.id,
                "created_by": workspace.created_by.id,
                "owner": workspace.owner.id,
                "name": workspace.name,
            }
            for workspace in results
        ]

        response["result"]["workspaces"] = WorkspaceReadSerializer(results, many=True).data

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request):
        """Update one or more fields on the authenticated user's profile.

        Accepted body fields (all optional): email, phone, first_name, last_name,
        password (requires current_password also be present).

        :param request: Authenticated HTTP request with fields to update in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response, or an error response describing the failure.
        :rtype: rest_framework.response.Response
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
                response["error"]["message"] = "Current password required when changing password."
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            auth = authenticate(email=request.user, password=request.data["current_password"])
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
