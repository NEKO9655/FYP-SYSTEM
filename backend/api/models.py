from django.db import models
from django.contrib.auth.models import User

# --- 基础模型 ---
class Programme(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.name

class Profile(models.Model):
    ROLE_CHOICES = (('student', 'Student'), ('lecturer', 'Lecturer'), ('coordinator', 'Coordinator'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, verbose_name="Full Name")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    programme = models.ForeignKey(Programme, on_delete=models.SET_NULL, null=True, blank=True)
    phone_no = models.CharField(max_length=50, blank=True, null=True)
    student_id_no = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.user.username

class FYPProject(models.Model):
    FYP_STAGE_CHOICES = (('FYP1', 'Final Year Project 1'), ('FYP2', 'Final Year Project 2'))
    student = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'})
    student_matric_id = models.CharField(max_length=50, blank=True, verbose_name="Student ID")
    title = models.CharField(max_length=255)
    supervisor = models.ForeignKey(User, related_name='supervised_projects', on_delete=models.SET_NULL, null=True, limit_choices_to={'profile__role': 'lecturer'})
    co_supervisor = models.ForeignKey(User, related_name='cosupervised_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    examiner = models.ForeignKey(User, related_name='examined_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    programme = models.ForeignKey(Programme, on_delete=models.SET_NULL, null=True, blank=True)
    fyp_stage = models.CharField(max_length=10, choices=FYP_STAGE_CHOICES, default='FYP1')
    def __str__(self):
        return self.title

# --- 资源模型 (保留原有) ---
class PresentationDay(models.Model):
    date = models.DateField()
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='presentation_days') 
    class Meta:
        unique_together = ('date', 'programme')

class Venue(models.Model):
    name = models.CharField(max_length=100)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='venues')
    class Meta:
        unique_together = ('name', 'programme')

# --- 新增的强绑定 Slot 模型 ---
class PresentationSlot(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    date = models.DateField()
    venue_name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('programme', 'date', 'venue_name')

# --- 业务模型 ---
class TimetableBooking(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'lecturer'})
    project = models.ForeignKey(FYPProject, on_delete=models.SET_NULL, null=True, blank=True)
    examiner = models.ForeignKey(User, related_name='examiner_bookings', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    venue = models.CharField(max_length=100, blank=True)
    class Meta:
        unique_together = ('start_time', 'venue')
        ordering = ['start_time']

class TimetableSlot(models.Model):
    project = models.ForeignKey(FYPProject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    examiners = models.ManyToManyField(User, limit_choices_to={'profile__role': 'lecturer'})
    venue = models.CharField(max_length=100, blank=True)

class Announcements(models.Model):
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE, db_column='coordinator_user_id')
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, blank=True) 
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'announcements'

class Feedback(models.Model):
    submission = models.ForeignKey('Submissions', on_delete=models.CASCADE, db_column='submission_id')
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, db_column='lecturer_user_id')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta:
        db_table = 'feedback'

class Submissions(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_submissions', db_column='student_user_id')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='student_submissions', db_column='supervisor_user_id')
    co_supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='co_supervisor_user_id')
    student_name = models.CharField(max_length=255)
    student_id_no = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=50, blank=True, null=True)
    programme = models.CharField(max_length=100)
    semester = models.CharField(max_length=50)
    project_category = models.CharField(max_length=50)
    proposed_project_title = models.TextField()
    detail_description = models.TextField(blank=True, null=True)
    detail_problem = models.TextField(blank=True, null=True)
    detail_value = models.TextField(blank=True, null=True)
    detail_scope = models.TextField(blank=True, null=True)
    detail_similar_system = models.TextField(blank=True, null=True)
    detail_features = models.TextField(blank=True, null=True)
    document_path = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'submissions'

class MilestoneForms(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, db_column='lecturer_user_id')
    student_name = models.CharField(max_length=255)
    student_id_no = models.CharField(max_length=50, blank=True, null=True)
    fyp_title = models.TextField()
    supervisor_name = models.CharField(max_length=255)
    class Meta:
        db_table = 'milestone_forms'

class MilestoneEntries(models.Model):
    form = models.ForeignKey(MilestoneForms, on_delete=models.CASCADE, db_column='form_id', related_name='entries')
    milestone_number = models.IntegerField()
    milestone_name = models.CharField(max_length=255, default='')
    max_marks = models.IntegerField(default=0)
    score = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    class Meta:
        db_table = 'milestone_entries'
        ordering =['milestone_number']

class SupervisorQuotas(models.Model):
    lecturer = models.OneToOneField(User, on_delete=models.CASCADE, db_column='lecturer_user_id')
    quota_total = models.IntegerField()
    class Meta:
        db_table = 'supervisor_quotas'

class LecturerPreference(models.Model):
    lecturer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to=models.Q(profile__role='lecturer') | models.Q(profile__role='coordinator')
    )
    # 建议此处关联新的 PresentationSlot
    presentation_slot = models.ForeignKey(PresentationSlot, on_delete=models.CASCADE, null=True)
    unavailable_slots = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ('lecturer', 'presentation_slot')
        ordering = ['presentation_slot__date', 'lecturer__profile__full_name']

class RubricTemplate(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    template_data = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rubrics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

class RubricMarks(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('submitted', 'Submitted'), ('finalized', 'Finalized'))
    template = models.ForeignKey(RubricTemplate, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rubric_marks')
    evaluated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_marks')
    student_name = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255, null=True, blank=True)
    marks_data = models.JSONField()
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    evaluated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)