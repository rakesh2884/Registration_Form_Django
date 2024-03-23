from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User
from .serializers import userProfileSerializer

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = userProfileSerializer(data=request.data)
        username=request.data.get('username')
        password=request.data.get('password')
        user = User.objects.filter(username=username,password=password).exists()
        if user is not None:
            return Response({'message':'user already exists'})
        else:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username=request.data.get('username')
        password=request.data.get('password')
        user = User.objects.filter(username=username,password=password).exists()
        if user is not None:
            return Response({'message':'Login successful'},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)