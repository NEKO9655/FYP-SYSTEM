# backend/api/serializers.py
from rest_framework import serializers
from .models import User, FYPProject, TimetableBooking

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']

class FYPProjectSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)
    co_supervisor = UserSerializer(read_only=True)
    examiner = UserSerializer(read_only=True)

    class Meta:
        model = FYPProject
        fields = ['id', 'title', 'student', 'student_matric_id', 'supervisor', 'co_supervisor', 'examiner' ]

class TimetableBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableBooking
        fields = ['id', 'lecturer', 'start_time', 'end_time', 'project']