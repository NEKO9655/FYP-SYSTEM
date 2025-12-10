# --- File: backend/api/models.py (FINAL & COMPLETE) ---

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- 1. NEW: Course Model ---
class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

# --- 2. UPDATED: Profile Model ---
class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('coordinator', 'Coordinator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, verbose_name="Full Name")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# --- 3. UPDATED: FYPProject Model ---
class FYPProject(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'})
    student_matric_id = models.CharField(max_length=50, blank=True, verbose_name="Student ID")
    title = models.CharField(max_length=255)
    supervisor = models.ForeignKey(User, related_name='supervised_projects', on_delete=models.SET_NULL, null=True, limit_choices_to={'profile__role': 'lecturer'})
    co_supervisor = models.ForeignKey(User, related_name='cosupervised_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    examiner = models.ForeignKey(User, related_name='examined_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.title

# --- Other models remain unchanged ---
class TimetableBooking(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'lecturer'})
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    project = models.ForeignKey(FYPProject, on_delete=models.SET_NULL, null=True, blank=True)
    examiner = models.ForeignKey(User, related_name='booking_examiner', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'lecturer'})
    
    def __str__(self):
        if self.project:
            return f"Booking for '{self.project.title}' by {self.lecturer.username}"
        return f"Availability for {self.lecturer.username}"
  
class TimetableSlot(models.Model):
    project = models.ForeignKey(FYPProject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    examiners = models.ManyToManyField(User, limit_choices_to={'profile__role': 'lecturer'})
    venue = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Slot for {self.project.title} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"