from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, FYPProject, TimetableBooking, TimetableSlot

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role']

class FYPProjectSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)
    co_supervisor = UserSerializer(read_only=True)
    examiner = UserSerializer(read_only=True)

    class Meta:
        model = FYPProject
        fields = ['id', 'title', 'student', 'student_matric_id', 'supervisor', 'co_supervisor', 'examiner']


class TimetableBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableBooking
        fields = ['id', 'lecturer', 'start_time', 'end_time', 'project', 'examiner']


class TimetableSlotSerializer(serializers.ModelSerializer):
    project = FYPProjectSerializer(read_only=True)

    class Meta:
        model = TimetableSlot
        fields = ['id', 'project', 'start_time', 'end_time', 'venue']