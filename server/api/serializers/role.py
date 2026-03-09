from rest_framework import serializers
from ..models import WorkspaceRole, MemberRole


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceRole name and pay_rate fields.

    The workspace field is intentionally excluded because callers pass
    workspace_id directly in the request body to keep naming consistent
    with other endpoints.
    """

    class Meta:
        """Meta options for RoleSerializer."""

        model = WorkspaceRole
        fields = [
            "name",
            "pay_rate",
        ]

        extra_kwargs = {"name": {"required": False}, "pay_rate": {"required": False}}
