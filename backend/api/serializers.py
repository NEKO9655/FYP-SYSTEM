from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Programme, Profile, FYPProject, TimetableBooking, 
    TimetableSlot, PresentationDay, Venue, PresentationSlot,
    Submissions, Feedback, MilestoneForms, MilestoneEntries, 
    SupervisorQuotas, Announcements, LecturerPreference,
    RubricTemplate, RubricMarks
)

class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = ['id', 'name', 'code']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)
    student_id_no = serializers.CharField(source='profile.student_id_no', read_only=True)
    programme_id = serializers.IntegerField(source='profile.programme.id', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'role', 'student_id_no', 'programme_id']

class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.profile.full_name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.profile.full_name', read_only=True, allow_null=True)
    
    # 这两行是正确的，确保它们存在
    supervisor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    co_supervisor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Submissions
        fields = '__all__'
        read_only_fields = ['student', 'status']

class FYPProjectSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.profile.full_name')
    supervisor_name = serializers.ReadOnlyField(source='supervisor.profile.full_name')
    co_supervisor_name = serializers.ReadOnlyField(source='co_supervisor.profile.full_name')
    examiner_name = serializers.ReadOnlyField(source='examiner.profile.full_name')
    class Meta:
        model = FYPProject
        fields = '__all__'

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

class TimetableSlotSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    student_name = serializers.CharField(source='project.student.profile.full_name', read_only=True)
    student_id = serializers.CharField(source='project.student_matric_id', read_only=True)
    
    class Meta:
        model = TimetableSlot
        fields = ['id', 'project', 'project_title', 'student_name', 'student_id', 'start_time', 'end_time', 'venue']

class AnnouncementSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.CharField(source='coordinator.profile.full_name', read_only=True)
    class Meta:
        model = Announcements
        fields = ['id', 'title', 'content', 'created_at', 'coordinator_name']
        read_only_fields = ['coordinator']

class FeedbackSerializer(serializers.ModelSerializer):
    lecturer_name = serializers.CharField(source='lecturer.profile.full_name', read_only=True)
    class Meta:
        model = Feedback
        fields = ['id', 'submission', 'lecturer', 'lecturer_name', 'comment', 'created_at', 'is_read']
        read_only_fields = ['lecturer']

class MilestoneEntriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneEntries
        fields = ['id', 'form', 'milestone_number', 'milestone_name', 'max_marks', 'score', 'status']
        read_only_fields = ['id', 'form']

class MilestoneFormsSerializer(serializers.ModelSerializer):
    entries = MilestoneEntriesSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = MilestoneForms
        fields = '__all__'
        read_only_fields = ['lecturer']
        
    def get_progress(self, obj):
        approved_count = obj.entries.filter(status='approved').count()
        return f"{approved_count} / 8"

    def update(self, instance, validated_data):
        entries_data = self.context['request'].data.get('entries', [])
        
        instance.student_name = validated_data.get('student_name', instance.student_name)
        instance.fyp_title = validated_data.get('fyp_title', instance.fyp_title)
        instance.save()

        for entry_data in entries_data:
            entry_id = entry_data.get('id', None)
            if entry_id:
                try:
                    entry = MilestoneEntries.objects.get(id=entry_id, form=instance)
                    score_value = entry_data.get('score', entry.score)
                    entry.score = int(score_value) if score_value is not None and score_value != '' else None
                    entry.status = entry_data.get('status', entry.status)
                    entry.save()
                except (MilestoneEntries.DoesNotExist, ValueError):
                    pass
        
        return instance

class PresentationSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentationSlot  # 这里引用的名字必须和导入的一模一样
        fields = ['id', 'date', 'venue_name'] # 确保这些字段在 models.py 的 PresentationSlot 中存在
        read_only_fields = ['programme']
        
class SimplePresentationDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentationDay
        fields = ['id', 'date']

class LecturerPreferenceSerializer(serializers.ModelSerializer):
    # 这里也必须更新！
    presentation_slot = PresentationSlotSerializer(read_only=True)
    presentation_slot_id = serializers.PrimaryKeyRelatedField(
        queryset=PresentationSlot.objects.all(), 
        source='presentation_slot', 
        write_only=True
    )

    class Meta:
        model = LecturerPreference
        fields =['id', 'lecturer', 'presentation_slot', 'presentation_slot_id', 'unavailable_slots']
        read_only_fields = ['lecturer']

class RubricTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricTemplate
        fields = '__all__'
        read_only_fields = ['created_by']

class RubricMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricMarks
        fields = '__all__'
        read_only_fields = ['evaluated_by']