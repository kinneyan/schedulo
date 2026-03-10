from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import RoleSerializer
from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
)

### WORKSPACE ROLE ENDPOINTS ###


class CreateRole(APIView):
    """API view for creating a new role in a workspace."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new WorkspaceRole in the given workspace.

        Requires manage_workspace_roles permission. Accepted body fields:
        workspace_id (required), name (optional), pay_rate (optional).

        :param request: Authenticated HTTP request with workspace_id and optional
            role fields in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
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

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(
                user=request.user, workspace=request.data["workspace_id"]
            )
            MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
                member=member,
                manage_workspace_roles=True,
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        workspace_role = WorkspaceRole.objects.create(workspace=workspace)

        if "name" in serializer.validated_data:
            workspace_role.name = serializer.validated_data["name"]
        if "pay_rate" in serializer.validated_data:
            workspace_role.pay_rate = serializer.validated_data["pay_rate"]

        workspace_role.save()

        return Response(response, status=status.HTTP_201_CREATED)


class DeleteWorkspaceRole(APIView):
    """API view for deleting a workspace role. Requires manage_workspace_roles."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Delete a WorkspaceRole by ID.

        :param request: Authenticated HTTP request containing workspace_role_id
            in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on deletion, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Workspace role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify role exists
        try:
            role = WorkspaceRole.objects.get(id=request.data["workspace_role_id"])
        except WorkspaceRole.DoesNotExist:
            response["error"][
                "message"
            ] = "Workspace role does not exist or is not part of this workspace."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Get role's workspace
        try:
            workspace = Workspace.objects.get(id=role.workspace.id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            MemberPermissions.objects.get(
                workspace=workspace, member=member, manage_workspace_roles=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # delete role
        role = WorkspaceRole.objects.get(id=request.data["workspace_role_id"]).delete()
        return Response(response, status=status.HTTP_200_OK)


class ModifyWorkspaceRole(APIView):
    """API view for updating a workspace role's name or pay rate."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Update name and/or pay_rate for an existing WorkspaceRole.

        Requires manage_workspace_roles permission. Accepted body fields:
        workspace_role_id (required), name (optional), pay_rate (optional).

        :param request: Authenticated HTTP request with workspace_role_id and
            optional update fields in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response, or an error response describing the failure.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Workspace role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify role exists
        try:
            workspace_role = WorkspaceRole.objects.get(
                pk=request.data["workspace_role_id"]
            )
        except WorkspaceRole.DoesNotExist:
            response["error"]["message"] = "Workspace role does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify workspace exists; this shouldnt ever fail but have to get the workspace
        try:
            workspace = Workspace.objects.get(pk=workspace_role.workspace.id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            MemberPermissions.objects.get(
                workspace=workspace, member=member, manage_workspace_roles=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # modify role
        if "name" in serializer.validated_data:
            workspace_role.name = serializer.validated_data["name"]
        if "pay_rate" in serializer.validated_data:
            workspace_role.pay_rate = serializer.validated_data["pay_rate"]

        workspace_role.save()

        return Response(response, status=status.HTTP_200_OK)


class GetWorkspaceRoles(APIView):
    """API view for listing all roles in a workspace."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Return a list of all WorkspaceRoles in the given workspace.

        :param request: Authenticated HTTP request containing workspace_id in the body.
        :type request: rest_framework.request.Request
        :return: List of roles with id, name, and pay_rate, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Verify body contains required fields
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        results = WorkspaceRole.objects.filter(workspace=workspace)

        role_list = [
            {
                "id": role.id,
                "name": role.name,
                "pay_rate": role.pay_rate,
            }
            for role in results
        ]

        response["roles"] = role_list

        return Response(response, status=status.HTTP_200_OK)


class GetMemberRoles(APIView):
    """API view for listing all WorkspaceRoles assigned to a specific member."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Return the list of WorkspaceRoles assigned to a given workspace member.

        :param request: Authenticated HTTP request containing member_id in the body.
        :type request: rest_framework.request.Request
        :return: List of roles with id, name, and pay_rate, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "member_id" not in request.data:
            response["error"]["message"] = "Member ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify that member exists
        try:
            member = WorkspaceMember.objects.get(id=request.data["member_id"])
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # get list of roles
        member_roles = MemberRole.objects.filter(member=member)
        results = WorkspaceRole.objects.filter(pk__in=member_roles)

        role_list = [
            {
                "id": role.id,
                "name": role.name,
                "pay_rate": role.pay_rate,
            }
            for role in results
        ]

        response["roles"] = role_list

        return Response(response, status=status.HTTP_200_OK)


### MEMBER ROLE ENDPOINTS ###


class AddMemberRole(APIView):
    """API view for assigning a WorkspaceRole to a workspace member."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Assign a WorkspaceRole to a workspace member.

        Requires manage_workspace_roles permission. Accepted body fields:
        member_id (required), workspace_role_id (required).

        :param request: Authenticated HTTP request with member_id and
            workspace_role_id in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on assignment, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "member_id" not in request.data:
            response["error"]["message"] = "Member ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Role ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify member exists
        try:
            modify_member = WorkspaceMember.objects.get(id=request.data["member_id"])
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Get workspace
        workspace = Workspace.objects.get(id=modify_member.workspace.id)

        # Verify user has permissions to manage workspace roles
        try:
            request_member = WorkspaceMember.objects.get(
                user=request.user, workspace=workspace
            )
            MemberPermissions.objects.get(
                workspace=workspace, member=request_member, manage_workspace_roles=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # Verify that role exists and is part of workspace
        try:
            workspace_role = WorkspaceRole.objects.get(
                id=request.data["workspace_role_id"], workspace=workspace
            )
        except WorkspaceRole.DoesNotExist:
            response["error"][
                "message"
            ] = "Role is not part of this workspace or does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify that member does not already have this role
        try:
            MemberRole.objects.get(
                member=request.data["member_id"],
                workspace_role=request.data["workspace_role_id"],
            )
        except MemberRole.DoesNotExist:
            # add role to member if they did not have it
            MemberRole.objects.create(
                member=modify_member, workspace_role=workspace_role
            )
            return Response(response, status=status.HTTP_201_CREATED)

        # member already had role
        response["error"]["message"] = "Member already has this role."
        return Response(response, status=status.HTTP_409_CONFLICT)


class RemoveMemberRole(APIView):
    """API view for removing a WorkspaceRole from a workspace member."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Remove a WorkspaceRole from a workspace member.

        Requires manage_workspace_roles permission. Accepted body fields:
        member_id (required), workspace_role_id (required).

        :param request: Authenticated HTTP request with member_id and
            workspace_role_id in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on removal, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "member_id" not in request.data:
            response["error"]["message"] = "Member ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Role ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify member exists
        try:
            modify_member = WorkspaceMember.objects.get(id=request.data["member_id"])
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Get workspace
        workspace = Workspace.objects.get(id=modify_member.workspace.id)

        # Verify user has permissions to manage workspace roles
        try:
            request_member = WorkspaceMember.objects.get(
                user=request.user, workspace=workspace
            )
            MemberPermissions.objects.get(
                workspace=workspace, member=request_member, manage_workspace_roles=True
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission modify roles in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # Verify that role exists and is part of workspace
        try:
            WorkspaceRole.objects.get(
                id=request.data["workspace_role_id"], workspace=workspace
            )
        except WorkspaceRole.DoesNotExist:
            response["error"][
                "message"
            ] = "Role is not part of this workspace or does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify that member already has this role
        try:
            MemberRole.objects.get(
                member=request.data["member_id"],
                workspace_role=request.data["workspace_role_id"],
            )
        except MemberRole.DoesNotExist:
            # add role to member if they did not have it
            response["error"]["message"] = "Member does not have this role."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # remove role
        MemberRole.objects.get(
            member=request.data["member_id"],
            workspace_role=request.data["workspace_role_id"],
        ).delete()
        return Response(response, status=status.HTTP_200_OK)
