from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from datetime import date

from ..serializers import ShiftSerializer, ModifyShiftSerializer, ShiftReadSerializer
from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
    Shift,
)


class ShiftView(APIView):
    """API view for shifts."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, shift_id):
        """Get details for shift in url params
        returns:
        result {
            id: shift id
            member(can be None): {
                id: member id
                first_name: first name
                last_name: last name
            }
            role: {
                id: role id
                name: role name
            }
            start_time: shift start time
            end_time: shift end time
            open: Boolean (if shift has member assigned)
        }

        """

        response = {"error": {}}

        # ensure shift id is valid
        try:
            shift = (
                Shift.objects.select_related("member__user", "role")
                .prefetch_related("member__member_roles__workspace_role")
                .get(pk=shift_id)
            )
        except Shift.DoesNotExist:
            response["error"]["message"] = "Shift could not be found."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # get workspace from shift
        workspace = shift.workspace

        # Verify user is part of workspace and has perms to manage schedules
        try:
            _ = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
        except WorkspaceMember.DoesNotExist:
            response["error"][
                "message"
            ] = "You must be a member of the workspace to retrieve shift details."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        data = ShiftReadSerializer(shift).data
        response["result"] = data

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, shift_id):
        """Update one or more fields on an existing Shift.

        Requires manage_schedules permission. Accepted body fields: member_id (optional), role_id (optional), start_time (optional),
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
            response["error"][
                "message"
            ] = "Invalid request data, start or end time invalid."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # ensure shift id is valid
        try:
            shift = Shift.objects.get(pk=shift_id)
        except Shift.DoesNotExist:
            response["error"]["message"] = "Shift could not be found."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # get workspace from shift
        workspace = shift.workspace

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
                response["error"][
                    "message"
                ] = "Member does not exist or is not part of workspace."
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            shift.member = member
            shift.open = False
            shift.save()

        if "role_id" in request.data:
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

            shift.role = role
            shift.save()

        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, shift_id):
        """Delete a Shift by ID.

        Requires manage_schedules permission. Accepted body fields:
        shift_id (required).

        :param request: Authenticated HTTP request containing shift_id in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on deletion, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        # ensure shift id is valid
        try:
            shift = Shift.objects.get(pk=shift_id)
        except Shift.DoesNotExist:
            response["error"]["message"] = "Shift could not be found."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # get workspace from shift
        workspace = shift.workspace

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

        # delete shift
        shift = Shift.objects.get(id=shift_id).delete()
        return Response(response, status=status.HTTP_200_OK)


class ShiftFilterView(APIView):
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
        results = (
            Shift.objects.filter(**filters)
            .select_related("member__user", "role")
            .prefetch_related("member__member_roles__workspace_role")
        )

        data = ShiftReadSerializer(results, many=True).data
        response["result"] = data

        return Response(response, status=status.HTTP_200_OK)
