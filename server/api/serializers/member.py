from .base import DynamicFieldsSerializer
from ..models import WorkspaceMember, User
from .users import UserReadSerializer, UserDetailedReadSerializer
from .role import MemberRoleReadSerializer


class MemberReadSerializer(DynamicFieldsSerializer):
    user = UserReadSerializer(read_only=True)
    member_roles = MemberRoleReadSerializer(many=True, read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ["id", "user", "member_roles"]

    # override to_representation to create a list without each workspace role being labeled, and to flatten user name
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "user" in data:
            user = data.pop("user")
            data.update(user)
        if "member_roles" in data:
            data["member_roles"] = [mr["workspace_role"] for mr in data["member_roles"]]
        return data


class MemberDetailedReadSerializer(DynamicFieldsSerializer):
    user = UserDetailedReadSerializer(
        read_only=True, fields=["first_name", "last_name", "phone", "email"]
    )
    member_roles = MemberRoleReadSerializer(many=True, read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ["id", "user", "member_roles"]

    # override to_representation to create a list without each workspace role being labeled, and to flatten user name
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "user" in data:
            user = data.pop("user")
            data.update(user)
        if "member_roles" in data:
            data["member_roles"] = [mr["workspace_role"] for mr in data["member_roles"]]
        return data
