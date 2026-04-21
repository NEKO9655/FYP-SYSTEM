# --- File: backend/api/models.py (终极缝合版) ---
from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. 核心基础设施 (保留现有功能)
# ==========================================

class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.name

class Profile(models.Model):
    ROLE_CHOICES = (('student', 'Student'), ('lecturer', 'Lecturer'), ('coordinator', 'Coordinator'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, verbose_name="Full Name")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- 整合队友 Users 表中的特有字段 ---
    phone_no = models.CharField(max_length=50, blank=True, null=True)
    student_id_no = models.CharField(max_length=50, blank=True, null=True) # 对应队友的 student_id_no
    programme = models.CharField(max_length=100, blank=True, null=True)    # 对应队友的 programme

    def __str__(self):
        return self.user.username

# ==========================================
# 2. 时间表模块 (保留现有功能)
# ==========================================

class FYPProject(models.Model):
    FYP_STAGE_CHOICES = (('FYP1', 'Final Year Project 1'), ('FYP2', 'Final Year Project 2'))
    student = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'})
    student_matric_id = models.CharField(max_length=50, blank=True, verbose_name="Student ID")
    title = models.CharField(max_length=255)
    supervisor = models.ForeignKey(User, related_name='supervised_projects', on_delete=models.SET_NULL, null=True, limit_choices_to={'profile__role': 'lecturer'})
    co_supervisor = models.ForeignKey(User, related_name='cosupervised_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    examiner = models.ForeignKey(User, related_name='examined_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    fyp_stage = models.CharField(max_length=10, choices=FYP_STAGE_CHOICES, default='FYP1')
    def __str__(self):
        return self.title

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

class PresentationDay(models.Model):
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='presentation_days')
    class Meta:
        unique_together = ('date', 'course')

class Venue(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='venues')
    class Meta:
        unique_together = ('name', 'course')

# ==========================================
# 3. 新功能模块 (从队友 wow.py 缝合)
# ==========================================

class Announcements(models.Model):
    # 关联到你的 User 系统
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE, db_column='coordinator_user_id')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'announcements' # 确保对接队友的 SQL 表

class Feedback(models.Model):
    # 假设关联到 Submissions 表
    submission = models.ForeignKey('Submissions', on_delete=models.CASCADE, db_column='submission_id')
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, db_column='lecturer_user_id')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta:
        db_table = 'feedback'

class Submissions(models.Model):
    """即 TRF Submission 核心表"""
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
    detail_description = models.TextField()
    detail_problem = models.TextField()
    detail_value = models.TextField()
    detail_scope = models.TextField()
    detail_similar_system = models.TextField()
    detail_features = models.TextField()
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
    score = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    class Meta:
        db_table = 'milestone_entries'

class SupervisorQuotas(models.Model):
    lecturer = models.OneToOneField(User, on_delete=models.CASCADE, db_column='lecturer_user_id')
    quota_total = models.IntegerField()
    class Meta:
        db_table = 'supervisor_quotas'