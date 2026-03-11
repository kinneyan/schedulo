from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from datetime import date

from ..serializers import ShiftRequestSerializer
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


class CreateShiftRequest(APIView):
    """API view for creating a new shift trade request"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new Shift swap request between sender and reciver.

        Both sender and reciver must be in the same workspace as the shifts. Accepted body fields:
        sender_shift_id(required), recipient_id(required), recipient_shift_id(optional)

        :param request: Authenticated HTTP request with shift details in the body.
        :type request: rest_framework.request.Request
        :return: Empty success response on creation, or an error response.
        :rtype: rest_framework.response.Response
        """
        response = {"error": {}}

        serializer = ShiftRequestSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"][
                "message"
            ] = "Invalid request data, sender shift and recipient are required."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        # get recipent workspace member
        try:
            recipient = WorkspaceMember.objects.get(pk=data["recipient_id"])
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Recipient does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # get workspace
        workspace = Workspace.objects.get(pk=recipient.workspace.id)
        
        # get sender shift
        try:
            sender_shift = Shift.objects.get(pk=data["sender_shift_id"])
        except Shift.DoesNotExist:
            response["error"]["message"] = "Sender shift does not exist."
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        # get sender workspace member
        try:
            sender = WorkspaceMember.objects.get(user=request.user, workspace=workspace)
        except WorkspaceMember.DoesNotExist:
            response["error"]["message"] = "Sender is not part of same workspace as recipient."
            return Response(response, status=status.HTTP_400_BAD_REQUEST) # TODO: ask drew if this is the right response type
        
        # get recipient shift if present
        recipient_shift_present = False
        recipient_shift = None
        if "recipient_shift_id" in data:
            try:
                recipient_shift_present = True
                recipient_shift = Shift.objects.get(pk=data["recipient_shift_id"])
            except Shift.DoesNotExist:
                response["error"]["message"] = "Recipient shift does not exist."
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
        # ensure sender and recipient are differet members
        if (sender == recipient):
            response["error"]["message"] = "Sender cannot be the same member as recipient."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        # ensure all objects are part of the same workspace
        if (sender.workspace != workspace):
            response["error"]["message"] = "Sender is not part of same workspace as recipient."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if (sender_shift.workspace != workspace):
            response["error"]["message"] = "Sender shift is not part of same workspace as recipient."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if (recipient_shift_present and recipient_shift.workspace != workspace):
            response["error"]["message"] = "Sender is not part of same workspace as recipient."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # ensure shifts are held by correct members
        if (sender_shift.open == True or sender_shift.member != sender):
            response["error"]["message"] = "Sender does not hold the sender shift."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if (recipient_shift_present and (recipient_shift.open == True or recipient_shift.member != recipient)):
            response["error"]["message"] = "Recipient does not hold the recipient shift."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        shift_request = ShiftRequest.objects.create(
            workspace=workspace,
            sender=sender,
            recipient=recipient,
            sender_shift=sender_shift,
        )

        if recipient_shift_present:
            shift_request.recipient_shift = recipient_shift
            shift_request.save()

        return Response(response, status=status.HTTP_201_CREATED)
        
