from rest_framework import serializers
from ..models import WorkspaceMember, User
from ..serializers import UserReadSerializer, MemberRoleReadSerializer

class MemberReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(read_only=True)
    member_roles = MemberRoleReadSerializer(many=True, read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ["id", "user", "member_roles"]

    # override to_representation to create a list without each workspace role being labeled, and to flatten user name
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = data.pop("user")
        data.update(user)
        data["member_roles"] = [mr["workspace_role"] for mr in data["member_roles"]]      
        return data