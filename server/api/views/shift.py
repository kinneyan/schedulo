from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from datetime import date

from ..serializers import ShiftSerializer, ModifyShiftSerializer
from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
    Shift,
)


class CreateShift(APIView):
    """API view for creating a new shift in a workspace."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Create a new Shift in the given workspace.

        Requires manage_schedules permission. Accepted body fields:
        workspace_id (required), role_id (required), start_time (required),
        end_time (required), member_id (optional).

        :param request: Authenticated HTTP request with shift details in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        serializer = ShiftSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data, start and end time are required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify body contains required fields
        if "role_id" not in request.data:
            response["error"]["message"] = "Role ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if "workspace_id" not in request.data:
            response["error"]["message"] = "Workspace ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Verify workspace exists
        try:
            workspace = Workspace.objects.get(pk=request.data["workspace_id"])
        except Workspace.DoesNotExist:
            response["error"]["message"] = "Workspace does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Verify user is part of workspace and has perms to manage schedules
        try:
            creator_member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
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
            role = WorkspaceRole.objects.get(pk=request.data["role_id"], workspace=workspace)
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
                response["error"]["message"] = "Member does not exist or is not part of workspace."
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


class ModifyShift(APIView):
    """API view for updating fields on an existing shift."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Update one or more fields on an existing Shift.

        Requires manage_schedules permission. Accepted body fields: shift_id
        (required), member_id (optional), role_id (optional), start_time (optional),
        end_time (optional).

        :param request: Authenticated HTTP request with shift_id and optional
            update fields in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response, or an error response describing the failure.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        serializer = ModifyShiftSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data, start and end time are required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Ensure that shift ID present
        if "shift_id" not in request.data:
            response["error"]["message"] = "Shift ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # ensure shift id is valid
        try:
            shift = Shift.objects.get(pk=request.data["shift_id"])
        except Shift.DoesNotExist:
            response["error"]["message"] = "Shift could not be found."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # get workspace from shift
        workspace = Workspace.objects.get(pk=shift.workspace.id)

        # Verify user is part of workspace and has perms to manage schedules
        try:
            creator_member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            MemberPermissions.objects.get(member=creator_member, manage_schedules=True)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permissions to manage schedules in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # Make included modifications

        # seprate if for both start and end included since they have to be checked to not be invalid
        if ("start_time" in serializer.validated_data) and (
            "end_time" in serializer.validated_data
        ):
            start_time = serializer.validated_data["start_time"]
            end_time = serializer.validated_data["end_time"]

            if start_time > end_time:
                response["error"]["message"] = "Start time cannot be after end time."
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            shift.start_time = start_time
            shift.end_time = end_time
            shift.save()
        elif "start_time" in serializer.validated_data:
            start_time = serializer.validated_data["start_time"]
            end_time = shift.end_time

            if start_time > end_time:
                response["error"]["message"] = "Start time cannot be after end time."
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            shift.start_time = start_time
            shift.save()
        elif "end_time" in serializer.validated_data:
            start_time = shift.start_time
            end_time = serializer.validated_data["end_time"]

            if start_time > end_time:
                response["error"]["message"] = "End time cannot be before start time."
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            shift.end_time = end_time
            shift.save()

        if "member_id" in request.data:
            try:
                member = WorkspaceMember.objects.get(
                    pk=request.data["member_id"], workspace=workspace
                )
            except WorkspaceMember.DoesNotExist:
                response["error"]["message"] = "Member does not exist or is not part of workspace."
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            shift.member = member
            shift.open = False
            shift.save()

        if "role_id" in request.data:
            # Verify role exists and is part of workspace
            try:
                role = WorkspaceRole.objects.get(pk=request.data["role_id"], workspace=workspace)
            except WorkspaceRole.DoesNotExist:
                response["error"][
                    "message"
                ] = "Workspace role does not exist or is not part of workspace."
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            shift.role = role
            shift.save()

        return Response(response, status=status.HTTP_200_OK)


class DeleteShift(APIView):
    """API view for deleting an existing shift."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Delete a Shift by ID.

        Requires manage_schedules permission. Accepted body fields:
        shift_id (required).

        :param request: Authenticated HTTP request containing shift_id in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on deletion, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # Ensure that shift ID present
        if "shift_id" not in request.data:
            response["error"]["message"] = "Shift ID is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # ensure shift id is valid
        try:
            shift = Shift.objects.get(pk=request.data["shift_id"])
        except Shift.DoesNotExist:
            response["error"]["message"] = "Shift could not be found."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # get workspace from shift
        workspace = Workspace.objects.get(pk=shift.workspace.id)

        # Verify user is part of workspace and has perms to manage schedules
        try:
            creator_member = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
            MemberPermissions.objects.get(member=creator_member, manage_schedules=True)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        except MemberPermissions.DoesNotExist:
            response["error"][
                "message"
            ] = "You do not have permissions to manage schedules in this workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # delete shift
        shift = Shift.objects.get(id=request.data["shift_id"]).delete()
        return Response(response, status=status.HTTP_200_OK)


class GetShifts(APIView):
    """API view for querying shifts across the authenticated user's workspaces."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Return shifts matching the provided filters.

        Results are always scoped to workspaces the authenticated user belongs to.
        All filter fields are optional but at least one should be provided.
        Accepted body fields: shift_id, member_id, role_id, workspace_id, open,
        created_by_id, range_start (Y-m-d), range_end (Y-m-d).

        :param request: Authenticated HTTP request with optional filter fields
            in the body.
        :type request: rest_framework.request.Request
        :return: List of matching shifts, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        filters = {}
        if "shift_id" in request.data:
            filters["id"] = request.data["shift_id"]
        if "member_id" in request.data:
            filters["member"] = request.data["member_id"]
        if "role_id" in request.data:
            filters["role"] = request.data["role_id"]
        if "workspace_id" in request.data:
            filters["workspace"] = request.data["workspace_id"]
        if "open" in request.data:
            filters["open"] = request.data["open"]
        if "created_by_id" in request.data:
            filters["created_by"] = request.data["created_by_id"]

        try:
            if "range_start" in request.data and "range_end" in request.data:
                filters["start_time__date__range"] = (
                    datetime.strptime(request.data["range_start"], "%Y-%m-%d").date(),
                    datetime.strptime(request.data["range_end"], "%Y-%m-%d").date(),
                )
            elif "range_start" in request.data:
                filters["start_time__date__range"] = (
                    datetime.strptime(request.data["range_start"], "%Y-%m-%d").date(),
                    date.max,
                )
            elif "range_end" in request.data and "range_end" in request.data:
                filters["start_time__date__range"] = (
                    date.min,
                    datetime.strptime(request.data["range_end"], "%Y-%m-%d").date(),
                )
        except Exception:
            response["error"]["message"] = "Date range value is invalid."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # add users workspaces to filters
        filters["workspace__in"] = Workspace.objects.filter(
            pk__in=WorkspaceMember.objects.filter(user=request.user)
        )

        # search by filters
        results = Shift.objects.filter(**filters)

        shift_list = [
            {
                "id": shift.id,
                "member_id": getattr(shift.member_id, "id", None),
                "role_id": shift.role.id,
                "workspace_id": shift.workspace.id,
                "open": shift.open,
                "created_by_id": shift.created_by.id,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
            }
            for shift in results
        ]

        response["shifts"] = shift_list

        return Response(response, status=status.HTTP_200_OK)
