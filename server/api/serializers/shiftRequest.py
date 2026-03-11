from rest_framework import serializers
from ..models import ShiftRequest


class ShiftRequestSerializer(serializers.ModelSerializer):
    """Serializer for ShiftRequest creation that requires sender_shift_id and recipient_id, optionally takes recipient_shift_id"""
    
    sender_shift_id = serializers.IntegerField(required=True)
    recipient_id = serializers.IntegerField(required=True)
    recipient_shift_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = ShiftRequest
        fields = ["sender_shift_id", "recipient_id", "recipient_shift_id"]
