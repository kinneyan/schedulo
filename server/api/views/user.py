from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class GetUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = {}

        response['email'] = request.user.email
        response['phone'] = request.user.phone
        response['first_name'] = request.user.first_name
        response['last_name'] = request.user.last_name

        return Response(response, status=status.HTTP_200_OK)
