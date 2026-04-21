# --- File: backend/api/serializers.py (补全修正版) ---
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Course, Profile, FYPProject, TimetableBooking, 
    TimetableSlot, PresentationDay, Venue, 
    Submissions, Feedback, MilestoneForms, MilestoneEntries, SupervisorQuotas
)

# --- 1. 基础序列化器 ---
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

# --- 2. 队友功能：TRF Submissions ---
class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.profile.full_name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.profile.full_name', read_only=True)
    class Meta:
        model = Submissions
        fields = '__all__'
        read_only_fields = ['student', 'status']

# --- 3. 队友功能：Feedback ---
class FeedbackSerializer(serializers.ModelSerializer):
    lecturer_name = serializers.CharField(source='lecturer.profile.full_name', read_only=True)
    class Meta:
        model = Feedback
        fields = '__all__'

# --- 4. 队友功能：Milestones (记事本) ---
class MilestoneEntriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneEntries
        fields = '__all__'

class MilestoneFormsSerializer(serializers.ModelSerializer):
    entries = MilestoneEntriesSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = MilestoneForms
        fields = '__all__'

    def get_progress(self, obj):
        approved_count = obj.entries.filter(status='approved').count()
        return f"{approved_count} / 8"

# --- 5. 原有功能：时间表与预约 ---
class FYPProjectSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    class Meta:
        model = FYPProject
        fields = '__all__'
    def get_student_name(self, obj):
        try: return obj.student.profile.full_name or obj.student.username
        except: return "N/A"
    def get_supervisor_name(self, obj):
        try: return obj.supervisor.profile.full_name or obj.supervisor.username
        except: return "N/A"

class TimetableBookingSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    student_name = serializers.CharField(source='project.student.profile.full_name', read_only=True)
    student_id = serializers.CharField(source='project.student_matric_id', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.profile.full_name', read_only=True)
    examiner_name = serializers.CharField(source='examiner.profile.full_name', read_only=True)
    class Meta:
        model = TimetableBooking
        fields = '__all__'
        read_only_fields = ['lecturer']

# --- 【关键补全】：TimetableSlotSerializer ---
class TimetableSlotSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    student_name = serializers.CharField(source='project.student.profile.full_name', read_only=True)
    student_id = serializers.CharField(source='project.student_matric_id', read_only=True)
    
    supervisor_id = serializers.IntegerField(source='project.supervisor.id', read_only=True)
    co_supervisor_id = serializers.IntegerField(source='project.co_supervisor.id', read_only=True, allow_null=True)
    
    class Meta:
        model = TimetableSlot
        fields = '__all__'

# --- 6. 其他设置 ---
class PresentationDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentationDay
        fields = '__all__'
        read_only_fields = ['course']

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'
        read_only_fields = ['course']