# --- File: backend/api/serializers.py ---

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

# --- 重点修改部分：TimetableBookingSerializer ---
class TimetableBookingSerializer(serializers.ModelSerializer):
    # 增加快捷字段，方便前端网格显示
    project_title = serializers.CharField(source='project.title', read_only=True)
    student_name = serializers.CharField(source='project.student.profile.full_name', read_only=True)
    # 增加考官姓名显示
    examiner_name = serializers.CharField(source='examiner.profile.full_name', read_only=True)
    # 发起者设为只读
    lecturer = UserSerializer(read_only=True)

    class Meta:
        model = TimetableBooking
        fields = ['id', 'lecturer', 'project', 'project_title', 'student_name', 'examiner', 'examiner_name', 'start_time', 'end_time', 'venue']