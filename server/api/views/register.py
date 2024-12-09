from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import CustomTokenObtainPairSerializer, RegisterUserSerializer
from ..models import User

class Register(APIView):
    def post(self, request):
        response = {"error": {}}

        serializer = RegisterUserSerializer(data=request.data)
        if not serializer.is_valid():
            if "email" in serializer.errors and serializer.errors["email"][0].code == "unique":
                response["error"]["code"] = 409
                response["error"]["message"] = "Account with this email already exists"
                return Response(response, status=status.HTTP_409_CONFLICT)
                
            response["error"]["code"] = 400
            response["error"]["message"] = "Invalid request data"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                phone=serializer.validated_data["phone"]
            )
            user.save()

            token_serializer = CustomTokenObtainPairSerializer(data={"email": user.email, "password": serializer.validated_data["password"]})
            token_serializer.is_valid()
            response["access"] = token_serializer.validated_data["access"]
            response["refresh"] = token_serializer.validated_data["refresh"]
            return Response(response, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            response["error"]["code"] = 500
            response["error"]["message"] = "Internal server error"
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
