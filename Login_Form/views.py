from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from Login.settings import SECRET_KEY
from jwt import encode
import re
from .serializers import userProfileSerializer


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = userProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            password=serializer.data['password']

            if len(password) < 8:
                return Response({'message':'Make sure your password is at lest 8 letters'}) 
            elif re.search('[0-9]',password) is None:
                return Response({'message':'Make sure your password has a number in it'})
            elif re.search('[A-Z]',password) is None: 
                return Response({'message':'Make sure your password has a capital letter in it'})
            elif re.search('[^a-zA-Z0-9]',password) is None:
                return Response({'message':'Make sure your password has a special character in it'}) 
            elif password!=serializer.data['confirm_password']:
                return Response({'message':'password not match'})
            user=User(username=serializer.data['username'],password=generate_password_hash(password),email=serializer.data['email'])
            user.save()
            return Response({'message':'Register successful'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message':'already exists'},status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = userProfileSerializer(data=request.data)
        username=request.data.get('username')
        password=request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            token = encode({"username":username,"password":password}, SECRET_KEY)
            return Response({'message':'Login successful','token':token},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)