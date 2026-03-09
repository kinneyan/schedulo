from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token serializer that adds the user's email to the token payload."""

    @classmethod
    def get_token(cls, user):
        """Generate a JWT token and embed the user's email in the payload.

        :param user: The authenticated user for whom the token is generated.
        :return: JWT token with the email claim added.
        :rtype: rest_framework_simplejwt.tokens.Token
        """
        token = super().get_token(user)
        token["email"] = user.email
        return token
