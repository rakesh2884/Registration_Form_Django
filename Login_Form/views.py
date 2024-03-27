from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password,check_password
from django.conf import settings
from django.core.mail import send_mail
from .models import User
from django_otp.oath import totp
import time
import threading
import re
from .serializers import userProfileSerializer,ChangePasswordSerializer,LoginSerializer,ForgotPasswordSerializer,ResetPasswordSerializer


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
            user=User(username=serializer.data['username'],password=make_password(password),email=serializer.data['email'])
            user.save()
            return Response({'message':'Register successful'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message':'already exists'},status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username=request.data.get('username')
            password=request.data.get('password')
            user = User.objects.get(username=username)
            if user and check_password(password,user.password):
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)
                return Response({'message':'Login successful','token':token},status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'message':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
            
class ChangePasswordView(UpdateAPIView):
    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            password=serializer.data['old_password']
            user = User.objects.get(username=username)
            if user and check_password(password,user.password):
                user.password=make_password(serializer.data['new_password'])
                user.save()
                return Response({'message':'password changed successfully'},status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'User not exist'},status=status.HTTP_400_BAD_REQUEST)
global arr
arr=[]
def f():
    arr.clear()
    threading.Timer(60, f).start()
class ForgetPasswordView(UpdateAPIView):
    def post(self, request, *args, **kwargs):
        serializer=ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            email=serializer.data['email']
            user=User.objects.get(username=username)
            if not user:
                return Response({'message':'User not exist'},status=status.HTTP_400_BAD_REQUEST)
            else:
                secret_key = b'12345678901234567890'
                now = int(time.time())
                otp=totp(key=secret_key, digits=6)
                f()
                arr.append(otp)
                
                subject = 'OTP to reset Password'
                message = "Hey ,"+ username + " To reset your password. Your OTP is : " + str(otp)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail( subject, message, email_from, recipient_list )
                return Response({'message':'OTP sent successfully'})
    def patch (self, request, *args, **kwargs):
        serializer=ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            OTP=serializer.data['OTP']
            new_password=serializer.data['new_password']
            user = User.objects.get(username=username)
            if user:
                if OTP in arr:
                    arr.clear()
                    user.password=make_password(new_password)
                    user.save()
                    return Response({'message':'password changed successfully'},status=status.HTTP_201_CREATED)
                else:
                    return Response ({'message':'invalid OTP'},status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'message':'user not exist'},status=status.HTTP_400_BAD_REQUEST)