# --- File: backend/api/serializers.py (FINAL REVISED VERSION) ---

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Profile, FYPProject, TimetableBooking, TimetableSlot

# --- CourseSerializer (remains unchanged) ---
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code']

# --- UserSerializer (remains unchanged) ---
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

# --- FYPProjectSerializer (remains unchanged) ---
class FYPProjectSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)
    co_supervisor = UserSerializer(read_only=True)
    examiner = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = FYPProject
        fields = ['id', 'title', 'student', 'student_matric_id', 'supervisor', 'co_supervisor', 'examiner', 'course', 'fyp_stage']

# --- TimetableBookingSerializer (remains unchanged) ---
class TimetableBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableBooking
        fields = ['id', 'lecturer', 'start_time', 'end_time', 'project', 'examiner']

# --- TimetableSlotSerializer (REVISED) ---
class TimetableSlotSerializer(serializers.ModelSerializer):
    # This nested serializer provides all project details, including student and supervisor info.
    project = FYPProjectSerializer(read_only=True)
    
    # --- THE CORE FIX IS HERE ---
    # We explicitly define the 'examiners' field to use the UserSerializer.
    # 'many=True' is crucial because it's a ManyToMany relationship.
    examiners = UserSerializer(many=True, read_only=True)

    class Meta:
        model = TimetableSlot
        # --- Ensure 'examiners' is included in the fields list ---
        fields = ['id', 'project', 'start_time', 'end_time', 'venue', 'examiners']