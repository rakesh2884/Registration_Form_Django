from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password,check_password
from django.conf import settings
from django.core.mail import send_mail
from .models import User, Task, Comments
from django_otp.oath import totp
import time
from django.core.files.storage import FileSystemStorage
import os
import re
from .serializers import userProfileSerializer,ChangePasswordSerializer,LoginSerializer,ForgotPasswordSerializer,ResetPasswordSerializer,\
    TaskAssignSerializer,TaskCheckSerializer,TaskUpdateSerializer,CommentsSerializer,CommentsCheckSerializer


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = userProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            username=serializer.data['username']
            password=serializer.data['password']
            image=request.FILES['image']
            fs = FileSystemStorage(location=settings.UPLOAD_FOLDER)
            filename = fs.save(image.name, image)
            i=os.path.join( settings.UPLOAD_FOLDER,image.name)
            try:
                user=User.objects.get(username=username)
                if user:
                    return Response({'message':'user already exist'},status=status.HTTP_400_BAD_REQUEST)
            except:    
                if len(password) < 8:
                    return Response({'message':'Make sure your password is at lest 8 letters'},status=status.HTTP_400_BAD_REQUEST) 
                elif re.search('[0-9]',password) is None:
                    return Response({'message':'Make sure your password has a number in it'},status=status.HTTP_400_BAD_REQUEST)
                elif re.search('[A-Z]',password) is None: 
                    return Response({'message':'Make sure your password has a capital letter in it'},status=status.HTTP_400_BAD_REQUEST)
                elif re.search('[^a-zA-Z0-9]',password) is None:
                    return Response({'message':'Make sure your password has a special character in it'},status=status.HTTP_400_BAD_REQUEST) 
                elif password!=serializer.data['confirm_password']:
                    return Response({'message':'password not match'},status=status.HTTP_400_BAD_REQUEST)
                user=User(username=username,password=make_password(password),email=serializer.data['email'],roles=serializer.data['roles'],image=i)
                user.save()
                return Response({'message':'Register successful'}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username=request.data.get('username')
            password=request.data.get('password')
            try:
                user = User.objects.get(username=username)
                if user and check_password(password,user.password):
                    refresh = RefreshToken.for_user(user)
                    token = str(refresh.access_token)
                    return Response({'message':'Login successful','token':token,'image':user.image},status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'message':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({'message':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
            
class ChangePasswordView(UpdateAPIView):
    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            password=serializer.data['old_password']
            try:
                user = User.objects.get(username=username)
                if user and check_password(password,user.password):
                    user.password=make_password(serializer.data['new_password'])
                    user.save()
                    return Response({'message':'password changed successfully'},status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({'message':'User not exist'},status=status.HTTP_400_BAD_REQUEST)
global arr
arr=[]
class ForgetPasswordView(UpdateAPIView):
    def post(self, request, *args, **kwargs):
        serializer=ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            email=serializer.data['email']
            try:
                user=User.objects.get(username=username)
                if user:
                    secret_key = b'12345678901234567890'
                    now = int(time.time())
                    otp=totp(key=secret_key, digits=6)
                    arr.append(otp)
                    
                    subject = 'OTP to reset Password'
                    message = "Hey ,"+ username + " To reset your password. Your OTP is : " + str(otp)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [email, ]
                    send_mail( subject, message, email_from, recipient_list )
                    return Response({'message':'OTP sent successfully'},status=status.HTTP_201_CREATED)                    
            except:
                return Response({'message':'User not exist'},status=status.HTTP_400_BAD_REQUEST)
                
    def patch (self, request, *args, **kwargs):
        serializer=ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            OTP=serializer.data['OTP']
            new_password=serializer.data['new_password']
            try:
                user = User.objects.get(username=username)
                if user:
                    if OTP in arr:
                        arr.remove(OTP)
                        user.password=make_password(new_password)
                        user.save()
                        return Response({'message':'password changed successfully'},status=status.HTTP_201_CREATED)
                    else:
                        return Response ({'message':'invalid OTP'},status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({'message':'user not exist'},status=status.HTTP_400_BAD_REQUEST)
class TaskView(APIView):
    def post(self, request, *args, **kwargs):
        serializer=TaskAssignSerializer(data=request.data)
        if serializer.is_valid():
            M_username=serializer.data['M_username']
            M_password=serializer.data['M_password']
            try:
                manager=User.objects.get(username=M_username)
                if manager and check_password(M_password,manager.password) and manager.roles==2:
                    E_username=serializer.data['E_username']
                    user_id=serializer.data['user_id']
                    try:
                        user=User.objects.get(username=E_username)
                        
                        if user and user.roles==1:
                            try:
                                if user_id==user.id:
                                    try:
                                        t=Task.objects.get(username=E_username)
                                        if t and t.task_status=="Pending":
                                            return Response({'message':'task still pending'},status=status.HTTP_400_BAD_REQUEST)
                                        else:
                                            tasks=Task(username=serializer.data['E_username'],task=serializer.data['task'],user_id=user_id)
                                            tasks.save()
                                            return Response({'message':'task assigned successfully'},status=status.HTTP_201_CREATED)  
                                    except:
                                        tasks=Task(username=serializer.data['E_username'],task=serializer.data['task'],user_id=serializer.data['user_id'])
                                        tasks.save()
                                        return Response({'message':'task assigned successfully'},status=status.HTTP_201_CREATED) 
                                else:
                                    return Response({'message':'Invalid user id'},status=status.HTTP_401_UNAUTHORIZED)
                            except:
                                return Response({'message':'Invalid user id'},status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            return Response({'message':'You cannot assign task to manager'},status=status.HTTP_401_UNAUTHORIZED)              
                    except:
                        return Response({'message':'the user you want to assign is not exist',})
                else:
                    return Response({'message':'Manager Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({'message':'dont have access'})
    def get(self, request, *args, **kwargs):
        serializer=TaskCheckSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            password=serializer.data['password']
            try:
                user=User.objects.get(username=username)
                if user and check_password(password,user.password):
                    try:
                        task=Task.objects.get(username=username)
                        if task:
                            return Response({'Your task is':task.task},status=status.HTTP_202_ACCEPTED)
                    except:
                        return Response({'message':'task not assigned yet'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message':'Invalid credentials'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'message':'user not exist'},status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        serializer=TaskUpdateSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            password=serializer.data['password']
            try:
                user=User.objects.get(username=username)
                if user and check_password(password,user.password):
                    try:
                        t=Task.objects.get(username=username)
                        t.task_status=serializer.data['task_status']
                        t.save()
                        return Response({'message':'task status changed'},status=status.HTTP_201_CREATED)
                    except Exception as e:
                        return Response({'message':'task not assign yet'})
                else:
                    return Response({'message':'Invalid credentials'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'message':'user not exist'},status=status.HTTP_400_BAD_REQUEST)
class CommentsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer=CommentsSerializer(data=request.data)
        if serializer.is_valid():
            M_username=serializer.data['M_username']
            M_password=serializer.data['M_password']        
            try:
                manager=User.objects.get(username=M_username)
                if manager and check_password(M_password,manager.password):
                    if manager.roles==2:
                        E_username=serializer.data['E_username']
                        user_id=serializer.data['user_id']
                        try:
                            user=User.objects.get(username=E_username)
                            task=Task.objects.get(username=E_username)
                            if task and user.roles==1:
                                if task.user_id==user_id:
                                    comments=Comments(username=serializer.data['E_username'],comments=serializer.data['comments'],user_id=user_id)
                                    comments.save()
                                    return Response({'message':'comment added successfully'},status=status.HTTP_201_CREATED)  
                                else:
                                    return Response({'message':'Invalid user id'},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({'message':'user does not have any task'},status=status.HTTP_400_BAD_REQUEST)
                        except:
                            return Response({'message':'user does not have any task'},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'message':'Do not have access to comment'})
                else:
                    return Response({'message':'Invalid credentials'},status=status.HTTP_201_CREATED)
            except:
                return Response({'message':'Invalid credentials'},status=status.HTTP_201_CREATED)
    def get(self, request, *args, **kwargs):
        serializer=CommentsCheckSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.data['username']
            password=serializer.data['password']
            try:
                user=User.objects.get(username=username)
                if user and check_password(password,user.password):
                    try:
                        comments=Comments.objects.get(username=username)
                        if comments:
                            return Response({'Comments':comments.comments},status=status.HTTP_202_ACCEPTED)
                    except:
                        return Response({'message':'No comments'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message':'Invalid credentials'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'message':'user not exist'},status=status.HTTP_400_BAD_REQUEST)