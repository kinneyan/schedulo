from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..serializers import WorkspaceSerializer
from ..models import Workspace, WorkspaceMember, User, MemberPermissions


class CreateWorkspace(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
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


class ModifyWorkspace(APIView):  # change name or owner, can only be done by owner.
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        workspace_id
        new_owner_id (optional)
        name (optional)
        """

        response = {"error": {}}

        serializer = WorkspaceSerializer(data=request.data)
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

        # Verify user is owner
        try:
            old_owner_member = WorkspaceMember.objects.get(
                user=request.user, workspace=request.data["workspace_id"]
            )
            MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
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
                    member=old_owner_member, workspace=request.data["workspace_id"]
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


class AddWorkspaceMember(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        body:
            added_user_id
            workspace_id
            pay_rate (optional)
            workspace_role_id (optional) # not yet implemented
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


class GetWorkspace(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        workspace_id (required)
        """
        response = {"error": {}}

        # Verify parameters contains required fields
        if request.GET.get("workspace_id") is None:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.GET.get("workspace_id"))
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
        """
        DECPRICATED
        # Verify user exists
        try:
            user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            response["error"]["message"] = "User does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        members = WorkspaceMember.objects.filter(user=user).values_list("workspace")
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
        """


class DeleteWorkspace(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    """
    workspace_id
    """

    def delete(self, request):
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

        # Verify user is owner
        try:
            owner_member = WorkspaceMember.objects.get(
                user=request.user, workspace=request.data["workspace_id"]
            )
            MemberPermissions.objects.get(
                workspace=request.data["workspace_id"],
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
