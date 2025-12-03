from rest_framework import viewsets
from django.core.mail import send_mail
from django.contrib.auth.models import User

from .models import FYPProject, TimetableBooking, TimetableSlot
from .serializers import UserSerializer, FYPProjectSerializer, TimetableBookingSerializer, TimetableSlotSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    ordering_fields = ['username']


class FYPProjectViewSet(viewsets.ModelViewSet):
    queryset = FYPProject.objects.all()
    serializer_class = FYPProjectSerializer
    
    ordering = ['student_matric_id']
    ordering_fields = ['student_matric_id', 'title']


class TimetableBookingViewSet(viewsets.ModelViewSet):
    queryset = TimetableBooking.objects.all()
    serializer_class = TimetableBookingSerializer
    ordering = ['start_time']
    ordering_fields = ['start_time']


class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.all()
    serializer_class = TimetableSlotSerializer
    
    ordering = ['start_time']
    ordering_fields = ['start_time']

def send_initial_notification(request):
    lecturers = User.objects.filter(profile__role='lecturer', is_active=True)
    
    recipient_list = [lecturer.email for lecturer in lecturers if lecturer.email]

    if recipient_list:
        send_mail(
            subject='Reminder: Please Submit Your FYP Availability',
            message='Dear Lecturers,\n\nPlease log in to the FYPHub to submit your available time slots for the upcoming presentations.\n\nThank you.',
            from_email='your-fyp-system-email@gmail.com',
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print(f"Successfully sent notifications to {len(recipient_list)} lecturers.")
    else:
        print("No lecturers with valid email addresses found.")