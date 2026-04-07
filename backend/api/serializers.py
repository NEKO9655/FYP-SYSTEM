# --- File: backend/api/serializers.py (修复 Student ID 版) ---

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Profile, FYPProject, TimetableBooking, TimetableSlot, PresentationDay

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role']

class FYPProjectSerializer(serializers.ModelSerializer):
    student_detail = UserSerializer(source='student', read_only=True)
    supervisor_detail = UserSerializer(source='supervisor', read_only=True)
    
    student_name = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    co_supervisor_name = serializers.SerializerMethodField()
    examiner_name = serializers.SerializerMethodField()

    class Meta:
        model = FYPProject
        fields = [
            'id', 'title', 'student', 'student_detail', 'student_name', 
            'student_matric_id', 'supervisor', 'supervisor_detail',
            'supervisor_name', 'co_supervisor', 'co_supervisor_name', 
            'examiner', 'examiner_name', 'course', 'fyp_stage'
        ]

    def get_student_name(self, obj):
        try: return obj.student.profile.full_name or obj.student.username
        except: return "N/A"

    def get_supervisor_name(self, obj):
        try: return obj.supervisor.profile.full_name or obj.supervisor.username
        except: return "N/A"

    def get_co_supervisor_name(self, obj):
        try: return obj.co_supervisor.profile.full_name or obj.co_supervisor.username
        except: return "N/A"

    def get_examiner_name(self, obj):
        try: return obj.examiner.profile.full_name or obj.examiner.username
        except: return "N/A"

# 用于正式排程的大表（Coordinator视角）
class TimetableSlotSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    student_name = serializers.CharField(source='project.student.profile.full_name', read_only=True)
    student_id = serializers.CharField(source='project.student_matric_id', read_only=True)
    
    supervisor_id = serializers.IntegerField(source='project.supervisor.id', read_only=True)
    co_supervisor_id = serializers.IntegerField(source='project.co_supervisor.id', read_only=True, allow_null=True)
    examiner_id = serializers.IntegerField(source='project.examiner.id', read_only=True)

    class Meta:
        model = TimetableSlot
        fields = [
            'id', 'project', 'project_title', 'student_name', 
            'student_id', 'supervisor_id', 'co_supervisor_id', 
            'examiner_id', 'start_time', 'end_time', 'venue'
        ]

# --- 重点修改：TimetableBookingSerializer ---
class TimetableBookingSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    student_name = serializers.CharField(source='project.student.profile.full_name', read_only=True)
    
    # 【新增这一行】：获取学号
    student_id = serializers.CharField(source='project.student_matric_id', read_only=True)
    
    examiner_name = serializers.CharField(source='examiner.profile.full_name', read_only=True)
    lecturer = UserSerializer(read_only=True)

    class Meta:
        model = TimetableBooking
        # 【确保 student_id 在 fields 列表中】
        fields = [
            'id', 'lecturer', 'project', 'project_title', 
            'student_name', 'student_id', 'examiner', 
            'examiner_name', 'start_time', 'end_time', 'venue'
        ]

class PresentationDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentationDay
        fields = ['id', 'date', 'course']
        read_only_fields = ['course']