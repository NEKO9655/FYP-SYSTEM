from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.models import User
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import moment

from .models import FYPProject, TimetableBooking, TimetableSlot
from .serializers import UserSerializer, FYPProjectSerializer, TimetableBookingSerializer, TimetableSlotSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    ordering_fields = ['username']

class FYPProjectViewSet(viewsets.ModelViewSet):
    queryset = FYPProject.objects.all().order_by('student_matric_id')
    serializer_class = FYPProjectSerializer

class TimetableBookingViewSet(viewsets.ModelViewSet):
    queryset = TimetableBooking.objects.all().order_by('start_time')
    serializer_class = TimetableBookingSerializer

class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.all().order_by('start_time')
    serializer_class = TimetableSlotSerializer

@api_view(['POST'])
def send_initial_notification(request):
    try:
        lecturers = User.objects.filter(profile__role='lecturer', is_active=True)
        
        recipient_list = [lecturer.email for lecturer in lecturers if lecturer.email]

        if recipient_list:
            send_mail(
                subject='Reminder: Please Submit Your FYP Availability',
                message='Dear Lecturers,\n\nPlease log in to the FYPHub to submit your available time slots for the upcoming presentations.\n\nThank you.',
                from_email='your-fyp-system-email@uts.edu.my',
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            success_message = f"Successfully sent notifications to {len(recipient_list)} lecturers."
            print(success_message)
            return Response({'status': 'success', 'message': success_message})
        
        else:
            no_recipients_message = "No lecturers with valid email addresses found. No emails were sent."
            print(no_recipients_message)
            return Response({'status': 'success', 'message': no_recipients_message})

    except Exception as e:
        error_message = f"An error occurred while sending emails: {str(e)}"
        print(error_message)
        return Response({'status': 'error', 'message': error_message}, status=500)