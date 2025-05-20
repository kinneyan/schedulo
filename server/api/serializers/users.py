from rest_framework import serializers
from ..models import User


class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]

        # Stop unique email validation for login serializer
        extra_kwargs = {
            "email": {"validators": []},
        }


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "phone"]

        extra_kwargs = {
            "email": {"required": True},
            "password": {"required": True, "write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone": {"required": True},
        }
