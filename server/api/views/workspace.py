from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import WorkspaceSerializer, ShiftSerializer, RoleSerializer, WorkspaceReadSerializer, MemberReadSerializer
from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    MemberRole,
    WorkspaceRole,
    Shift,
    ShiftRequest,
)


class WorkspaceView(APIView):
    """API view for creating a new workspace owned by the authenticated user."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new workspace and add the authenticated user as its owner.

        :param request: Authenticated HTTP request containing an optional name
            in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # get name from request using serializer
        serializer = WorkspaceSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # create new workspace
        workspace = Workspace.objects.create(
            created_by=request.user, owner=request.user
        )

        # set name if present
        if not (serializer.data.get("name", None) is None):
            name = serializer.validated_data["name"]
            workspace.name = name
            workspace.save()

        # add creator of workspace as owner of the new workspace
        workspace_member = WorkspaceMember.objects.create(
            workspace=workspace, user=request.user, added_by=request.user
        )

        # create permissions for owner
        MemberPermissions.objects.create(
            workspace=workspace,
            member=workspace_member,
            is_owner=True,
            manage_workspace_members=True,
            manage_workspace_roles=True,
            manage_schedules=True,
            manage_time_off=True,
        )

        return Response(response, status=status.HTTP_201_CREATED)

    """API view for renaming a workspace or transferring ownership. Owner only."""

    def put(self, request, workspace_id=None):
        """Update the name or owner of a workspace.

        Requires the authenticated user to be the workspace owner.
        Aceepected parameters fields: workspace_id (required)
        Accepted body fields: new_owner_id (optional), name (optional).

        :param request: Authenticated HTTP request with workspace_id and optional
            new_owner_id or name in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response, or an error response describing the failure.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        serializer = WorkspaceSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify body contains required fields
        if workspace_id is None:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is owner
        try:
            old_owner_member = WorkspaceMember.objects.get(
                user=request.user, workspace=workspace
            )
            MemberPermissions.objects.get(
                workspace=workspace,
                member=old_owner_member,
                is_owner=True,
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission modify this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # Update Workspace
        if "new_owner_id" in request.data:  # update workspace owner
            # Check new owner
            try:
                new_owner_member = WorkspaceMember.objects.get(
                    user=request.data["new_owner_id"], workspace=workspace
                )
                new_owner_perms = MemberPermissions.objects.get(member=new_owner_member)

                # set current owner to no longer be owner
                old_owner_perms = MemberPermissions.objects.get(
                    member=old_owner_member, workspace=workspace
                )

                if (
                    new_owner_perms == old_owner_perms
                ):  # cannot set new owner to current
                    response["error"][
                        "message"
                    ] = "Member is already owner of this workspace."
                    return Response(response, status=status.HTTP_409_CONFLICT)

                old_owner_perms.is_owner = False
                old_owner_perms.save()

                # set new owner to be owner
                new_owner_perms.is_owner = True
                new_owner_perms.manage_workspace_members = True
                new_owner_perms.manage_workspace_roles = True
                new_owner_perms.manage_schedules = True
                new_owner_perms.manage_time_off = True
                new_owner_perms.save()

                # update owner id in workspace
                workspace.owner = User.objects.get(pk=request.data["new_owner_id"])
                workspace.save()

            except MemberPermissions.DoesNotExist:
                response["error"]["message"] = "Could not find member with provided ID."
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            except WorkspaceMember.DoesNotExist:
                response["error"]["message"] = "Could not find member with provided ID."
                return Response(response, status=status.HTTP_404_NOT_FOUND)

        if not (serializer.data.get("name", None) is None):  # update name
            workspace.name = serializer.validated_data["name"]
            workspace.save()

        return Response(response, status=status.HTTP_200_OK)

    """API view for retrieving details about a workspace the user belongs to."""

    def get(self, request, workspace_id=None):
        """Return workspace details 

        :param request: Authenticated HTTP request with workspace_id as a query
            parameter.
        :type request: rest_framework.request.Request
        :return: Workspace name, owner info, membership level, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Verify parameters contains required fields
        if workspace_id is None:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exists."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is member of workspace
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "User is not a member of this workspace."
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        data = WorkspaceReadSerializer(workspace).data
        response["result"] = data

        return Response(response, status=status.HTTP_200_OK)

    """API view for deleting a workspace. Requires the authenticated user to be owner."""

    def delete(self, request, workspace_id=None):
        """Delete a workspace by ID.

        :param request: Authenticated HTTP request containing workspace_id in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on deletion, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Verify body contains required fields
        if workspace_id is None:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is owner
        try:
            owner_member = WorkspaceMember.objects.get(
                user=request.user, workspace=workspace
            )
            MemberPermissions.objects.get(
                workspace=workspace,
                member=owner_member,
                is_owner=True,
            )
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permission modify this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        workspace.delete()
        return Response(response, status=status.HTTP_200_OK)


class WorkspaceMembersView(APIView):
    """API view managing members of a workspace."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_id):
        """Add a user to a workspace as a new member.

        Accepted body fields: added_user_id (required), workspace_id (required),
        pay_rate (optional).

        :param request: Authenticated HTTP request with added_user_id in the body, and workspace_id in url params
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # ensure workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is permitted to add members to workspace
        try:
            workspace_member = WorkspaceMember.objects.get(
                user=request.user, workspace=workspace
            )
            MemberPermissions.objects.get(
                member=workspace_member,
                workspace=workspace,
                manage_workspace_members=True,
            )
        except MemberPermissions.DoesNotExist:
            response["error"] = (
                "You do not have permission to add members to this workspace"
            )
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # get added user
        try:
            added_user = User.objects.get(pk=request.data["added_user_id"])
        except User.DoesNotExist:
            response["error"]["message"] = "Added user does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        if not (
            WorkspaceMember.objects.filter(
                user=added_user,
                workspace=workspace,
            ).exists()
        ):  # check if user is already member of workspace
            workspace_member = WorkspaceMember.objects.create(
                workspace=workspace,
                user=added_user,
                added_by=request.user,
            )

            if "pay_rate" in request.data:
                workspace_member.pay_rate = request.data["pay_rate"]
                workspace_member.save()

            MemberPermissions.objects.create(
                workspace=workspace,
                member=workspace_member,
            )

            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response["error"] = "User is already member of this workspace"
            return Response(response, status=status.HTTP_409_CONFLICT)

    def get(self, request, workspace_id):
        """
        workspace_id (required)
        """
        response = {"error": {}}

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exists."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is member of workspace
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "User is not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        member_results = (
            WorkspaceMember.objects.filter(workspace=workspace)
        )
        data = MemberReadSerializer(member_results, many=True).data

        response["result"] = data
        return Response(response, status=status.HTTP_200_OK)


class WorkspaceShiftsView(APIView):
    """API view managing shifts of a workspace."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_id):
        """Create a new Shift in the given workspace.

        Requires manage_schedules permission. Accepted body fields:
        role_id (required), start_time (required),
        end_time (required), member_id (optional).

        :param request: Authenticated HTTP request with workspace_id in url and shift details in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        serializer = ShiftSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"][
                "message"
            ] = "Invalid request data, start and end time are required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify body contains required fields
        if "role_id" not in request.data:
            response["error"]["message"] = "Role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is part of workspace and has perms to manage schedules
        try:
            creator_member = WorkspaceMember.objects.get(
                user=request.user, workspace=workspace
            )
            MemberPermissions.objects.get(member=creator_member, manage_schedules=True)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permissions to manage schedules in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # Verify role exists and is part of workspace
        try:
            role = WorkspaceRole.objects.get(
                pk=request.data["role_id"], workspace=workspace
            )
        except WorkspaceRole.DoesNotExist:
            response["error"][
                "message"
            ] = "Workspace role does not exist or is not part of workspace."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify member is valid if present
        if "member_id" in request.data:
            try:
                member = WorkspaceMember.objects.get(
                    pk=request.data["member_id"], workspace=workspace
                )
            except WorkspaceMember.DoesNotExist:
                response["error"][
                    "message"
                ] = "Member does not exist or is not part of workspace."
                return Response(response, status=status.HTTP_404_NOT_FOUND)

        # verify dates are valid
        start_time = serializer.validated_data["start_time"]
        end_time = serializer.validated_data["end_time"]

        if start_time > end_time:
            response["error"]["message"] = "Start time cannot be after end time."
            return Response(
                response, status=status.HTTP_400_BAD_REQUEST
            )  # idk if this is the right status code but wtvr

        # could check if start time is before current time if we want to prevent creating shifts in the past, but i think we should allow that since a workplace might want to do that for recordkeeping or smth
        shift = Shift.objects.create(
            workspace=workspace,
            start_time=start_time,
            end_time=end_time,
            created_by=creator_member,
            role=role,
            open=True,
        )

        # Add member to shift if present
        if "member_id" in request.data:
            shift.member = member
            shift.open = False
            shift.save()

        return Response(response, status=status.HTTP_201_CREATED)

    def get(self, request, workspace_id):
        # TODO
        return None


class WorkspaceRolesView(APIView):
    """API view managing roles of a workspace."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_id):
        """Create a new WorkspaceRole in the given workspace.

        Requires manage_workspace_roles permission. Accepted body fields:
        name (optional), pay_rate (optional).

        :param request: Authenticated HTTP request with workspace_id in url and optional
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

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user has permissions to manage workspace roles
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            MemberPermissions.objects.get(
                workspace=workspace,
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

    def get(self, request, workspace_id):
        """Return a list of all WorkspaceRoles in the given workspace.

        :param request: Authenticated HTTP request containing workspace_id in the url.
        :type request: rest_framework.request.Request
        :return: List of roles with id, name, and pay_rate, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
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
