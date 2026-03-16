from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import WorkspaceSerializer
from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    MemberRole,
    WorkspaceRole,
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
        """Return workspace details and the authenticated user's membership role.

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

        # Get user's perms
        permissions = MemberPermissions.objects.get(workspace=workspace, member=member)

        if permissions.is_owner:
            response["membership"] = "owner"
        # UNCOMMENT WHEN MANAGER MEMBERSHIP ADDED!!
        # elif (permissions.IS_MANAGER):
        #   response["membership"] = "manager"
        else:
            response["membership"] = "employee"

        response["owner_name"] = (
            workspace.owner.first_name + " " + workspace.owner.last_name
        )
        response["owner_id"] = workspace.owner.id
        response["name"] = workspace.name
        response["workspace_id"] = workspace.id

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

        workspace = Workspace.objects.get(id=workspace.id).delete()
        return Response(response, status=status.HTTP_200_OK)


class AddWorkspaceMember(APIView):
    """API view for adding a user to a workspace. Requires manage_workspace_members."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add a user to a workspace as a new member.

        Accepted body fields: added_user_id (required), workspace_id (required),
        pay_rate (optional).

        :param request: Authenticated HTTP request with added_user_id and
            workspace_id in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Verify user is permitted to add members to workspace
        try:
            workspace_member = WorkspaceMember.objects.get(
                user=request.user, workspace=request.data["workspace_id"]
            )
            MemberPermissions.objects.get(
                member=workspace_member,
                workspace=request.data["workspace_id"],
                manage_workspace_members=True,
            )
        except MemberPermissions.DoesNotExist:
            response["error"] = (
                "You do not have permission to add members to this workspace"
            )
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        if not (
            WorkspaceMember.objects.filter(
                user=User.objects.get(pk=request.data["added_user_id"]),
                workspace=Workspace.objects.get(pk=request.data["workspace_id"]),
            ).exists()
        ):  # check if user is already member of workspace
            workspace_member = WorkspaceMember.objects.create(
                workspace=Workspace.objects.get(pk=request.data["workspace_id"]),
                user=User.objects.get(pk=request.data["added_user_id"]),
                added_by=request.user,
            )

            if "pay_rate" in request.data:
                workspace_member.pay_rate = request.data["pay_rate"]
                workspace_member.save()

            MemberPermissions.objects.create(
                workspace=Workspace.objects.get(pk=request.data["workspace_id"]),
                member=workspace_member,
            )

            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response["error"] = "User is already member of this workspace"
            return Response(response, status=status.HTTP_409_CONFLICT)

class GetWorkspaceMembers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        workspace_id (required)
        """
        response = {"error": {}}

        # Verify parameters contains required fields
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exists."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is member of workspace
        try:
            member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "User is not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # Get members of workspace
        member_results = (
            WorkspaceMember.objects.filter(workspace=workspace)
            .select_related("memberpermissions")
            .prefetch_related("memberrole_set__workspace_role")
        )

        members_list = []
        for member in member_results:
            roles_list = [
                {
                    "role_id": role.workspace_role.id,
                    "name": role.workspace_role.name,
                    "pay_rate": role.workspace_role.pay_rate,
                }
                for role in member.memberrole_set.all()
            ]

            entry = {
                "member_id": member.id,
                "user_id": member.user.id,
                "first_name": member.user.first_name,
                "last_name": member.user.last_name,
                "email": member.user.email,
                "roles": roles_list,
                "permissions": {
                    "is_owner": member.memberpermissions.is_owner,
                    "manage_workspace_members": member.memberpermissions.manage_workspace_members,
                    "manage_workspace_roles": member.memberpermissions.manage_workspace_roles,
                    "manage_schedules": member.memberpermissions.manage_schedules,
                    "manage_time_off": member.memberpermissions.manage_time_off,
                },
            }
            members_list.append(entry)

        response["members"] = members_list
        return Response(response, status=status.HTTP_200_OK)