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

        # try:

        # except: 
        #     response["error"]["code"] = 400
        #     response["error"]["message"] = "Invalid request data"
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)
