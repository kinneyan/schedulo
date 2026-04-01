from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime, timedelta, date, timezone

from ..serializers import ShiftRequestSerializer, ShiftRequestResponseSerializer
from ..models import (
    Workspace,
    WorkspaceMember,
    User,
    MemberPermissions,
    WorkspaceRole,
    MemberRole,
    Shift,
    ShiftRequest,
)


class ShiftRequestRespondView(APIView):
    """API view for responding to shift swap request"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, shift_request_id):
        """Respond to a shift swap request

        Request must be from the member who is the swap recipient. Accepted body fields:
        shift_request_id(url param)(required), accept(required)(boolean)

        :param request: Authenticated HTTP request with shift details in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        serializer = ShiftRequestResponseSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data, boolean accept field is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            shift_request = ShiftRequest.objects.get(pk=shift_request_id)
        except ShiftRequest.DoesNotExist:
            response["error"]["message"] = "Shift request does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        try:
            recipient = WorkspaceMember.objects.get(
                user=request.user.id, workspace=shift_request.workspace
            )
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "User is not a member of request workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        if recipient != shift_request.recipient:
            response["error"]["message"] = "Must be shift request recipient to accept the request."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        if shift_request.accepted == ShiftRequest.Status.PENDING:
            if data["accept"]:
                # ensure accepting the shift would not overlap with any shifts held by recipient, ingnores overlap with recipient shift if present as this shift would be traded
                # the +/- time deltas are to prevent overlaps being detected when shifts fall immidately before/after each other
                try:
                    shifts = Shift.objects.filter(
                        member=shift_request.recipient,
                        start_time__range=(
                            datetime.min.replace(tzinfo=timezone.utc),
                            shift_request.sender_shift.end_time - timedelta(seconds=1),
                        ),
                        end_time__range=(
                            shift_request.sender_shift.start_time + timedelta(seconds=1),
                            datetime.max.replace(tzinfo=timezone.utc),
                        ),
                    ).exclude(
                        pk=(
                            shift_request.recipient_shift.id
                            if shift_request.recipient_shift is not None
                            else None
                        )
                    )
                    if len(shifts) == 0:  # accept if there is no overlap
                        shift_request.accepted = ShiftRequest.Status.ACCEPTED
                        shift_request.save()
                    else:
                        response["error"][
                            "message"
                        ] = "Recipient cannot accept shift that overlaps with another shift they have."
                        return Response(response, status=status.HTTP_400_BAD_REQUEST)
                except Shift.DoesNotExist:  # accept if there is no overlap
                    shift_request.accepted = ShiftRequest.Status.ACCEPTED
                    shift_request.save()
            else:
                shift_request.accepted = ShiftRequest.Status.DECLINED
                shift_request.save()
        else:
            response["error"]["message"] = (
                "Shift request has already been responded to, current status is: "
                + shift_request.accepted
                + "."
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        return Response(response, status=status.HTTP_200_OK)


class ShiftRequestApproveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, shift_request_id):
        response = {"error": {}}

        serializer = ShiftRequestResponseSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"][
                "message"
            ] = "Invalid request data, boolean accepct field is required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # get shift request
        try:
            shift_request = ShiftRequest.objects.get(pk=shift_request_id)
        except ShiftRequest.DoesNotExist:
            response["error"]["message"] = "Shift request does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # get user making approval and perms
        try:
            user_member = WorkspaceMember.objects.get(
                user=request.user.id, workspace=shift_request.workspace
            )
            user_permissions = MemberPermissions.objects.get(member=user_member)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "You are not a member of request workspace."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # ensure user has perms to approve
        if not (user_permissions.manage_schedules or user_permissions.is_owner):
            response["error"]["message"] = "You do not have permission to approve this request."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        if (
            shift_request.accepted == ShiftRequest.Status.ACCEPTED
            and shift_request.approved == ShiftRequest.Status.PENDING
        ):
            if data["accept"]:
                # ensure accepting the shift would not overlap with any shifts held by recipient, ingnores overlap with recipient shift if present as this shift would be traded
                # the +/- time deltas are to prevent overlaps being detected when shifts fall immidately before/after each other
                shifts = Shift.objects.filter(
                    member=shift_request.recipient,
                    start_time__range=(
                        datetime.min.replace(tzinfo=timezone.utc),
                        shift_request.sender_shift.end_time - timedelta(seconds=1),
                    ),
                    end_time__range=(
                        shift_request.sender_shift.start_time + timedelta(seconds=1),
                        datetime.max.replace(tzinfo=timezone.utc),
                    ),
                ).exclude(
                    pk=(
                        shift_request.recipient_shift.id
                        if shift_request.recipient_shift is not None
                        else None
                    )
                )
                if len(shifts) != 0:  # prevent approving if overlap
                    response["error"][
                        "message"
                    ] = "Sender shift would conflict with one of recipient's shifts."
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                # check if recipient shift would overlap with one of sender's shifts
                if shift_request.recipient_shift is not None:
                    shifts = Shift.objects.filter(
                        member=shift_request.sender,
                        start_time__range=(
                            datetime.min.replace(tzinfo=timezone.utc),
                            shift_request.recipient_shift.end_time - timedelta(seconds=1),
                        ),
                        end_time__range=(
                            shift_request.recipient_shift.start_time + timedelta(seconds=1),
                            datetime.max.replace(tzinfo=timezone.utc),
                        ),
                    ).exclude(pk=(shift_request.sender_shift.id))

                    if len(shifts) != 0:  # prevent approving if overlap
                        response["error"][
                            "message"
                        ] = "Recipient shift would conflict with one of sender's shifts."
                        return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                shift_request.approved = ShiftRequest.Status.DECLINED
                shift_request.save()
                return Response(response, status=status.HTTP_200_OK)

        elif shift_request.approved != ShiftRequest.Status.PENDING:
            response["error"]["message"] = (
                "Shift request has already been approved/denied to, current status is: "
                + shift_request.approved
                + "."
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response["error"]["message"] = (
                "Shift request has not been accepted, current status is: "
                + shift_request.accepted
                + "."
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # no overlaps found, can approve
        shift_request.approved = ShiftRequest.Status.ACCEPTED
        shift_request.save()

        # assign sender shift to recipient
        shift_request.sender_shift.member = shift_request.recipient
        shift_request.sender_shift.save()

        # if recipient shift present, assign that shift to sender
        if shift_request.recipient_shift is not None:
            shift_request.recipient_shift.member = shift_request.sender
            shift_request.recipient_shift.save()

        return Response(response, status=status.HTTP_200_OK)
