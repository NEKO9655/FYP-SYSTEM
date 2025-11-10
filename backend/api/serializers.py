# backend/api/serializers.py
from rest_framework import serializers
from .models import User, FYPProject

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']

class FYPProjectSerializer(serializers.ModelSerializer):
    # 我们可以让它自动显示关联的 "student" 和 "supervisor" 的详细信息
    student = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)

    class Meta:
        model = FYPProject
        fields = ['id', 'title', 'student', 'supervisor']