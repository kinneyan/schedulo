from rest_framework import serializers
from ..models import Shift

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['start_time', 'end_time']

        extra_kwargs = {
            'start_time': {'required': True},
            'end_time': {'required': True},
        }

class ModifyShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['start_time', 'end_time']

        extra_kwargs = {
            'start_time': {'required': False},
            'end_time': {'required': False},
        }