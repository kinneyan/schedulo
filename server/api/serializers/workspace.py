from rest_framework import serializers
from ..models import Workspace

class CreateWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['name']

        extra_kwargs = {
            'name': {'required': False},
        }