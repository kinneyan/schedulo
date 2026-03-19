from rest_framework import serializers
from ..models import Shift
from .member import MemberReadSerializer
from .role import RoleReadSerializer



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

class ShiftReadSerializer(serializers.ModelSerializer):
    member = MemberReadSerializer(read_only=True, fields=["id", "user"])
    role = RoleReadSerializer(read_only=True, fields=["id", "name"])

    class Meta:
        model = Shift
        fields = ["id", "member", "role", "start_time", "end_time", "open"]