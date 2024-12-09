from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from ..serializers import LoginUserSerializer, CustomTokenObtainPairSerializer
from ..models import User

class Login(APIView):
    def post(self, request):
        response = {"error": {}}

        serializer = LoginUserSerializer(data=request.data)
        if not serializer.is_valid():
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = authenticate(email=email, password=password)
            if user is None:
                raise User.DoesNotExist
            
            serializer = CustomTokenObtainPairSerializer(data=request.data)
            if not serializer.is_valid():
                raise User.DoesNotExist
            
            response["access"] = serializer.validated_data["access"]
            response["refresh"] = serializer.validated_data["refresh"]

            return Response(response, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            response["error"]["code"] = 401
            response["error"]["message"] = "Incorrect email or password"

            return Response(response, status=status.HTTP_401_UNAUTHORIZED)