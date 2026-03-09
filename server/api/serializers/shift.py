from rest_framework import serializers
from ..models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for Shift creation that requires both start_time and end_time."""

    class Meta:
        """Meta options for ShiftSerializer."""

        model = Shift
        fields = ["start_time", "end_time"]

        extra_kwargs = {
            "start_time": {"required": True},
            "end_time": {"required": True},
        }


class ModifyShiftSerializer(serializers.ModelSerializer):
    """Serializer for Shift modification where start_time and end_time are optional."""

    class Meta:
        """Meta options for ModifyShiftSerializer."""

        model = Shift
        fields = ["start_time", "end_time"]

        extra_kwargs = {
            "start_time": {"required": False},
            "end_time": {"required": False},
        }
