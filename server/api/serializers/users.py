from rest_framework import serializers
from ..models import User

class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']

        # Stop unique email validation for login serializer
        extra_kwargs = {
            'email': {'validators': []},
        }
