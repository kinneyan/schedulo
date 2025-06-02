from rest_framework import serializers
from ..models import WorkspaceRole, MemberRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceRole
        fields = [
            "name",
            "pay_rate",
        ]  # workspace not included in serializer because it would need to be called 'workspace' rather than 'workspace_id', which would be inconsitent with other requests

        extra_kwargs = {"name": {"required": False}, "pay_rate": {"required": False}}
