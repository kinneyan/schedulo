from rest_framework import serializers
from ..models import User


class LoginUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[])

    class Meta:
        model = User
        fields = ["email", "password"]


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "phone"]

        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
            "password": {"required": True, "write_only": True, "allow_blank": False},
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "phone": {"required": True, "allow_blank": False},
        }
