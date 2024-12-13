from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class GetUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = {"error": {}}

        response['email'] = request.user.email
        response['phone'] = request.user.phone
        response['first_name'] = request.user.first_name
        response['last_name'] = request.user.last_name

        return Response(response, status=status.HTTP_200_OK)
    
    def put(self, request):
        response = {"error": {}}

        if "email" in request.data:
            try:
                validate_email(request.data["email"])
                request.user.email = request.data["email"]
                request.user.save()
            except ValidationError:
                response["error"]["email"] = "Invalid email format"
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if "password" in request.data:
            request.user.set_password(request.data["password"])
            request.user.save()

        if "phone" in request.data:
            request.user.phone = request.data["phone"]
            request.user.save()

        if "first_name" in request.data:
            request.user.first_name = request.data["first_name"]
            request.user.save()

        if "last_name" in request.data:
            request.user.last_name = request.data["last_name"]
            request.user.save()

        return Response(response, status=status.HTTP_200_OK)
