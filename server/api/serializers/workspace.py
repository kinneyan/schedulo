from rest_framework import serializers
from ..models import Workspace
from ..serializers import UserReadSerializer


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["name"]

        extra_kwargs = {
            "name": {"required": False},
        }

class WorkspaceReadSerializer(serializers.ModelSerializer):
    owner = UserReadSerializer(read_only=True)

    class Meta:
        model = Workspace
        fields = ["id", "name", "owner"]