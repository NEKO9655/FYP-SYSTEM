from rest_framework import viewsets
from .models import User, FYPProject, TimetableBooking, TimetableSlot
from .serializers import UserSerializer, FYPProjectSerializer, TimetableBookingSerializer, TimetableSlotSerializer
from django.core.mail import send_mail
from django.contrib.auth.models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class FYPProjectViewSet(viewsets.ModelViewSet):
    queryset = FYPProject.objects.all()
    serializer_class = FYPProjectSerializer
    
    ordering = ['student_matric_id'] 

class TimetableBookingViewSet(viewsets.ModelViewSet):
    queryset = TimetableBooking.objects.all()
    serializer_class = TimetableBookingSerializer

class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.all()
    serializer_class = TimetableSlotSerializer

    ordering = ['start_time'] 

def send_initial_notification(request):
    lecturers = User.objects.filter(profile__role='lecturer')
    recipient_list = [lecturer.email for lecturer in lecturers if lecturer.email]

    send_mail(
        'Reminder: Please Submit Your FYP Availability',
        'Dear Lecturers, please log in to the FYPHub to submit your available time slots for the upcoming presentations. Thank you.',
        'your-email@gmail.com',
        recipient_list,
        fail_silently=False,
    )