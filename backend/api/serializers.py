# --- File: backend/api/serializers.py (FINAL & COMPLETE) ---

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Profile, FYPProject, TimetableBooking, TimetableSlot

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)
    color = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role', 'color']
    def get_color(self, obj):
        colors = ['#FFADAD', '#FFD6A5', '#FDFFB6', '#CAFFBF', '#9BF6FF', '#A0C4FF', '#BDB2FF', '#FFC6FF']
        return colors[obj.id % len(colors)]

class FYPProjectSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)
    co_supervisor = UserSerializer(read_only=True)
    examiner = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = FYPProject
        # --- Add 'fyp_stage' to the fields list ---
        fields = ['id', 'title', 'student', 'student_matric_id', 'supervisor', 'co_supervisor', 'examiner', 'course', 'fyp_stage']

# --- Other serializers remain the same ---
class TimetableBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableBooking
        fields = ['id', 'lecturer', 'start_time', 'end_time', 'project', 'examiner']

class TimetableSlotSerializer(serializers.ModelSerializer):
    project = FYPProjectSerializer(read_only=True)
    class Meta:
        model = TimetableSlot
        fields = ['id', 'project', 'start_time', 'end_time', 'venue']