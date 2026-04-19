# --- File: backend/api/models.py ---
from django.db import models
from django.contrib.auth.models import User

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
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    fyp_stage = models.CharField(max_length=10, choices=FYP_STAGE_CHOICES, default='FYP1')
    def __str__(self):
        return self.title

class TimetableBooking(models.Model):
    # 发起预约的导师 (Supervisor)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'lecturer'})
    # 关联的项目 (包含学生信息)
    project = models.ForeignKey(FYPProject, on_delete=models.SET_NULL, null=True, blank=True)
    # 邀请的考官 (Examiner)
    examiner = models.ForeignKey(User, related_name='examiner_bookings', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    venue = models.CharField(max_length=100, blank=True)

    class Meta:
        # 防止同一时间、同一地点被重复预订 (双重预订预防)
        unique_together = ('start_time', 'venue')
        ordering = ['start_time']

    def __str__(self):
        return f"Booking: {self.project.title if self.project else 'Available'} ({self.venue})"

class TimetableSlot(models.Model):
    # 协调员最终确定的正式时间表
    project = models.ForeignKey(FYPProject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    examiners = models.ManyToManyField(User, limit_choices_to={'profile__role': 'lecturer'})
    venue = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"Slot for {self.project.title}"
    
class PresentationDay(models.Model):
    date = models.DateField(verbose_name="Presentation Date")
    # 关联课程：确保 BCS 协调员添加的天数，只有 BCS 的老师能看到
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='presentation_days')
    
    class Meta:
        unique_together = ('date', 'course') # 同一课程不能重复添加同一天
        ordering = ['date']

    def __str__(self):
        return f"{self.date} ({self.course.code})"

class Venue(models.Model):
    name = models.CharField(max_length=100) # 例如: CL3, CL4
    # 同样关联课程，确保 BCS 协调员只管理自己的教室
    course = models.ForeignKey(Course, on_object=models.CASCADE, related_name='venues')

    class Meta:
        unique_together = ('name', 'course')

    def __str__(self):
        return f"{self.name} ({self.course.code})"