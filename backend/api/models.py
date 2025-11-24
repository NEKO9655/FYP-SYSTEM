from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('coordinator', 'Coordinator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

class FYPProject(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    
    student_matric_id = models.CharField(max_length=50, blank=True, verbose_name="Student ID")
    
    title = models.CharField(max_length=255)
    supervisor = models.ForeignKey(User, related_name='supervised_projects', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'lecturer'})
    
    co_supervisor = models.ForeignKey(User, related_name='cosupervised_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'lecturer'})
    examiner = models.ForeignKey(User, related_name='examined_projects', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'lecturer'})

    def __str__(self):
        return self.title

class TimetableBooking(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'lecturer'})
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    project = models.ForeignKey(FYPProject, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.project:
            return f"Booking for '{self.project.title}' by {self.lecturer.username}"
        return f"Availability for {self.lecturer.username}"
  
class TimetableSlot(models.Model):
    project = models.ForeignKey(FYPProject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    examiners = models.ManyToManyField(User, limit_choices_to={'role': 'lecturer'})

    def __str__(self):
        return f"Slot for {self.project.title} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"