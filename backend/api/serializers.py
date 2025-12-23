# --- File: backend/api/serializers.py (FINAL FIXED VERSION) ---

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Profile, FYPProject, TimetableBooking, TimetableSlot

# --- 1. CourseSerializer (remains unchanged) ---
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code']

# --- 2. UserSerializer (REVISED AND FIXED) ---
# This single, complete UserSerializer now handles all user-related data.
class UserSerializer(serializers.ModelSerializer):
    # Fetch custom fields from the related Profile model
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)
    
    # Dynamically generate a color for each user
    color = serializers.SerializerMethodField()

    class Meta:
        model = User
        # --- The CORE FIX is here ---
        # The 'fields' list MUST include all necessary fields for the frontend.
        fields = ['id', 'username', 'full_name', 'email', 'role', 'color']

    # This method generates the color based on the user's ID
    def get_color(self, obj):
        # A list of pleasant, distinct colors
        colors = ['#FFADAD', '#FFD6A5', '#FDFFB6', '#CAFFBF', '#9BF6FF', '#A0C4FF', '#BDB2FF', '#FFC6FF']
        # Use the modulo operator to pick a color from the list, ensuring consistency
        return colors[obj.id % len(colors)]

# --- 3. Other serializers (remain unchanged) ---
# They will automatically use the updated UserSerializer.
class FYPProjectSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)
    co_supervisor = UserSerializer(read_only=True)
    examiner = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = FYPProject
        fields = ['id', 'title', 'student', 'student_matric_id', 'supervisor', 'co_supervisor', 'examiner', 'course', 'fyp_stage']

class TimetableBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableBooking
        fields = ['id', 'lecturer', 'start_time', 'end_time', 'project', 'examiner']

class TimetableSlotSerializer(serializers.ModelSerializer):
    project = FYPProjectSerializer(read_only=True)
    class Meta:
        model = TimetableSlot
        fields = ['id', 'project', 'start_time', 'end_time', 'venue']