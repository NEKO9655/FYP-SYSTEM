# --- File: backend/api/views.py (FINAL INTEGRATED & ROBUST VERSION) ---

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Q
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.conf import settings

from .models import Course, FYPProject, TimetableBooking, TimetableSlot
from .serializers import CourseSerializer, UserSerializer, FYPProjectSerializer, TimetableBookingSerializer, TimetableSlotSerializer

# --- ViewSets ---
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profile__role']

class FYPProjectViewSet(viewsets.ModelViewSet):
    queryset = FYPProject.objects.all().order_by('student_matric_id')
    serializer_class = FYPProjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'fyp_stage', 'supervisor']

class TimetableBookingViewSet(viewsets.ModelViewSet):
    queryset = TimetableBooking.objects.all().order_by('start_time')
    serializer_class = TimetableBookingSerializer

# --- UPDATED: TimetableSlotViewSet with dynamic filtering logic ---
class TimetableSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSlotSerializer

    def get_queryset(self):
        user = self.request.user
        
        # If the user is staff (like a coordinator), return all timetable slots
        if user.is_staff:
            return TimetableSlot.objects.all().order_by('start_time')
        
        # If the user is a lecturer, filter for their relevant slots
        if hasattr(user, 'profile') and user.profile.role == 'lecturer':
            # Use Q objects to find slots where the user is involved in any capacity
            return TimetableSlot.objects.filter(
                Q(project__supervisor=user) | 
                Q(project__examiner=user) | 
                Q(project__co_supervisor=user)
            ).distinct().order_by('start_time')
        
        # For any other role (like students), return an empty list for this endpoint
        return TimetableSlot.objects.none()

# --- Custom Function-Based API Views ---

# --- UPDATED: export_to_google_sheet with course filtering logic ---
@api_view(['POST'])
def export_to_google_sheet(request):
    user = request.user # Get the currently logged-in user

    try:
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"
        ]
        keyfile_path = os.path.join(settings.BASE_DIR, 'backend', 'client_secret.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
        client = gspread.authorize(creds)
        
        sheet_name = 'FYP_Schedule_Sheet'
        sheet = client.open(sheet_name).sheet1
        
        # Start with all slots
        slots_queryset = TimetableSlot.objects.all()

        # If the user is a coordinator and has an assigned course, filter the slots
        if hasattr(user, 'profile') and user.profile.role == 'coordinator' and user.profile.course:
            slots_queryset = slots_queryset.filter(project__course=user.profile.course)
        
        slots = slots_queryset.order_by('start_time')
        
        header = ['Date', 'Time Slot', 'Venue', 'Student', 'Project Title', 'Your Role']
        data_to_write = [header]
        
        for slot in slots:
            student_name = "N/A"
            if slot.project and slot.project.student and hasattr(slot.project.student, 'profile'):
                student_name = slot.project.student.profile.full_name or slot.project.student.username
            row = [
                str(slot.start_time.date()),
                f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
                slot.venue, student_name,
                slot.project.title if slot.project else 'N/A',
                'Supervisor' # Role logic needs enhancement in the future
            ]
            data_to_write.append(row)
        
        sheet.clear()
        sheet.update('A1', data_to_write)
        
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{sheet.spreadsheet.id}"
        return Response({'status': 'success', 'url': spreadsheet_url})
        
    except FileNotFoundError:
        return Response({'status': 'error', 'message': "CRITICAL: 'client_secret.json' not found."}, status=500)
    except gspread.exceptions.SpreadsheetNotFound:
        return Response({'status': 'error', 'message': f"Spreadsheet '{sheet_name}' not found."}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': f"An unexpected error occurred: {str(e)}"}, status=500)

@api_view(['POST'])
def send_initial_notification(request):
    try:
        lecturers = User.objects.filter(profile__role='lecturer', is_active=True)
        recipient_list = [lecturer.email for lecturer in lecturers if lecturer.email]

        if recipient_list:
            send_mail(
                subject='Reminder: Please Submit Your FYP Availability',
                message='Dear Lecturers,\n\nPlease log in to the FYPHub to submit your available time slots...\n\nThank you.',
                from_email='your-fyp-system-email@uts.edu.my',
                recipient_list=recipient_list,
                fail_silently=False,
            )
            success_message = f"Successfully sent notifications to {len(recipient_list)} lecturers."
            return Response({'status': 'success', 'message': success_message})
        else:
            no_recipients_message = "No lecturers with valid email addresses found."
            return Response({'status': 'success', 'message': no_recipients_message})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return Response({'status': 'error', 'message': error_message}, status=500)