from rest_framework import serializers
from ..models import MemberPermissions


class PermissionsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPermissions
        fields = [
            "is_owner",
            "manage_workspace_members",
            "manage_workspace_roles",
            "manage_schedules",
            "manage_time_off",
        ]
