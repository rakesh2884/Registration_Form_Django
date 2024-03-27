from rest_framework import serializers

from .models import User
class userProfileSerializer(serializers.ModelSerializer):
    user=serializers.StringRelatedField(read_only=True)
    confirm_password=serializers.CharField(required=True)
    class Meta:
        model=User
        fields="__all__"
        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
class ChangePasswordSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
class ForgotPasswordSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    email=serializers.EmailField(required=True)
class ResetPasswordSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    OTP=serializers.IntegerField(required=True )
    new_password=serializers.CharField(required=True)
    email=serializers.EmailField(required=True)
class TaskAssignSerializer(serializers.Serializer):
    M_username = serializers.CharField(required=True)
    M_password = serializers.CharField(required=True)
    E_username = serializers.CharField(required=True)
    user_id=serializers.IntegerField(required=True)
    task=serializers.CharField(required=True)
class TaskCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
class TaskUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    task_status=serializers.CharField(required=True)
