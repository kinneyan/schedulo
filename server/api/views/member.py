from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import MemberReadSerializer, PermissionsReadSerializer, MemberDetailedReadSerializer, ShiftReadSerializer

from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
    Shift,
)


class MemberView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        """
        Returns json in body with structure:
        {
            id: member id
            first_name: user first name
            last_name: user last name
            member_roles: [
                {
                    id: role id
                    name: role name
                },
                ...
            ]
        }
        """

        response = {"error": {}}

        # get member
        try:
            member = WorkspaceMember.objects.get(pk=member_id)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Could not find member with provided ID."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # ensure request is from user in same workspace
        try:
            _ = WorkspaceMember.objects.get(
                workspace=member.workspace, user=request.user
            )
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Must share a workspace to get member."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        data = MemberReadSerializer(member).data
        response["result"] = data

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, member_id):
        # TODO
        return None

    def delete(self, request, member_id):
        response = {"error": {}}

        # get member
        try:
            member = WorkspaceMember.objects.get(pk=member_id)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Could not find member with provided ID."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # verify user is part of workspace
        try:
            request_member = WorkspaceMember.objects.get(
                user=request.user, workspace=member.workspace
            )
        except WorkspaceMember.DoesNotExist:
            response["error"][
                "message"
            ] = "You must be a member of the same workspace to retreive member roles."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # verify request user has perms to view member shifts or is viewing own shifts
        perms = MemberPermissions.objects.get(member=request_member)
        if (
            perms.is_owner
            or perms.manage_workspace_members
            or member.id == request_member.id
        ):
            member.delete()
            return Response(response, status=status.HTTP_200_OK)
        else:
            response["error"][
                "message"
            ] = "You do not have permission to view this members roles."
            return Response(response, status=status.HTTP_403_FORBIDDEN)


class MemberPermissionsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        """Returns the perms of member in url param. User must be in same workspace

        result: {
            is_owner: Boolean
            manage_workspace_members: Boolean
            manage_workspace_roles: Boolean
            manage_schedules: Boolean
            manage_time_off: Boolean
        }
        """

        response = {"error": {}}

        # get member
        try:
            member = WorkspaceMember.objects.get(pk=member_id)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Could not find member with provided ID."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # ensure request is from user in same workspace
        try:
            _ = WorkspaceMember.objects.get(
                workspace=member.workspace, user=request.user
            )
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Must share a workspace to get member."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        permissions = MemberPermissions.objects.get(member=member)
        response["result"] = PermissionsReadSerializer(permissions).data

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, member_id):
        """Update permission flags for a specific workspace member.

        Requires manage_workspace_members permission. Accepted body fields:
        manage_workspace_members,
        manage_workspace_roles, manage_schedules, manage_time_off.

        :param request: Authenticated HTTP request with
            and optional permission flags in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response, or an error response describing the failure.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        try:
            member = WorkspaceMember.objects.get(pk=member_id)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Could not find member with provided ID."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user has required permissions
        try:
            workspace_member = WorkspaceMember.objects.get(
                user=request.user, workspace=member.workspace
            )
            permissions = MemberPermissions.objects.get(
                workspace=member.workspace,
                member=workspace_member,
                manage_workspace_members=True,
            )
        except (WorkspaceMember.DoesNotExist, MemberPermissions.DoesNotExist):
            response["error"][
                "message"
            ] = "You do not have permission to manage permissions for this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        try:
            # Check if permissions already exist
            permissions = MemberPermissions.objects.get(
                workspace=member.workspace, member=member
            )
        except MemberPermissions.DoesNotExist:
            # Create permissions if they do not exist
            permissions = MemberPermissions.objects.create(
                workspace=member.workspace,
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


class MemberRolesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, member_id):
        """Assign a WorkspaceRole to a workspace member.

        Requires manage_workspace_roles permission. Accepted body fields:
        workspace_role_id (required).

        :param request: Authenticated HTTP request with member_id in url and
            workspace_role_id in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on assignment, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Role ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify member exists
        try:
            modify_member = WorkspaceMember.objects.get(pk=member_id)
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
                pk=request.data["workspace_role_id"], workspace=workspace
            )
        except WorkspaceRole.DoesNotExist:
            response["error"][
                "message"
            ] = "Role is not part of this workspace or does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify that member does not already have this role
        try:
            MemberRole.objects.get(
                member=modify_member,
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

    def get(self, request, member_id):
        """Return the list of WorkspaceRoles assigned to a given workspace member.

        :param request: Authenticated HTTP request containing member_id in the body.
        :type request: rest_framework.request.Request
        :return: List of roles with id, name, and pay_rate, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Verify that member exists
        try:
            member = WorkspaceMember.objects.get(pk=member_id)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # verify user is part of workspace
        try:
            request_member = WorkspaceMember.objects.get(
                user=request.user, workspace=member.workspace
            )
        except WorkspaceMember.DoesNotExist:
            response["error"][
                "message"
            ] = "You must be a member of the same workspace to retreive member roles."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # verify request user has perms to view member roles or is viewing own roles
        # TODO: test for this once this is confirmed to be desired behavior
        perms = MemberPermissions.objects.get(member=request_member)
        if (
            perms.is_owner
            or perms.manage_workspace_members
            or perms.manage_workspace_roles
            or member.id == request_member.id
        ):
            data = MemberDetailedReadSerializer(member).data
            response["result"] = data["member_roles"]
            return Response(response, status=status.HTTP_200_OK)
        else:
            response["error"][
                "message"
            ] = "You do not have permission to view this members roles."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, member_id):
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

        if "workspace_role_id" not in request.data:
            response["error"]["message"] = "Role ID is required"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify member exists
        try:
            modify_member = WorkspaceMember.objects.get(pk=member_id)
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
                member=modify_member,
                workspace_role=request.data["workspace_role_id"],
            )
        except MemberRole.DoesNotExist:
            # add role to member if they did not have it
            response["error"]["message"] = "Member does not have this role."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # remove role
        MemberRole.objects.get(
            member=modify_member,
            workspace_role=request.data["workspace_role_id"],
        ).delete()
        return Response(response, status=status.HTTP_200_OK)


class MemberShiftsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        response = {"error": {}}

        # Verify that member exists
        try:
            member = WorkspaceMember.objects.get(pk=member_id)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Member does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # verify user is part of workspace
        try:
            request_member = WorkspaceMember.objects.get(
                user=request.user, workspace=member.workspace
            )
        except WorkspaceMember.DoesNotExist:
            response["error"][
                "message"
            ] = "You must be a member of the same workspace to retreive member roles."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # verify request user has perms to view member shifts or is viewing own shifts
        perms = MemberPermissions.objects.get(member=request_member)
        if (
            perms.is_owner
            or perms.manage_workspace_members
            or perms.manage_schedules
            or member.id == request_member.id
        ):
            shifts = Shift.objects.filter(member=member)
            data = ShiftReadSerializer(
                shifts, many=True, fields=["id", "role", "start_time", "end_time"]
            ).data
            response["result"] = data
            return Response(response, status=status.HTTP_200_OK)
        else:
            response["error"][
                "message"
            ] = "You do not have permission to view this members roles."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
