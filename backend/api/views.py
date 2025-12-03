# --- File: backend/api/views.py (FINAL REVISED VERSION) ---

from rest_framework import viewsets
from django.core.mail import send_mail
from django.contrib.auth.models import User # Django's built-in User model

# Import all your models and serializers
from .models import FYPProject, TimetableBooking, TimetableSlot
from .serializers import UserSerializer, FYPProjectSerializer, TimetableBookingSerializer, TimetableSlotSerializer

# --- ViewSets for your API ---

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # We filter by `is_active=True` to only show active users by default
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    # Allow ordering by username through URL parameters if needed
    ordering_fields = ['username']


class FYPProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FYP projects to be viewed or edited.
    """
    queryset = FYPProject.objects.all()
    serializer_class = FYPProjectSerializer
    
    # --- FIX #1: Ensure default ordering is applied correctly ---
    # The `ordering` attribute should be a list or tuple.
    ordering = ['student_matric_id']
    # It's good practice to also declare which fields are available for ordering.
    ordering_fields = ['student_matric_id', 'title']


class TimetableBookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing timetable bookings.
    """
    queryset = TimetableBooking.objects.all()
    serializer_class = TimetableBookingSerializer
    # Bookings should also be sorted by time
    ordering = ['start_time']
    ordering_fields = ['start_time']


class TimetableSlotViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing final presentation slots.
    """
    queryset = TimetableSlot.objects.all()
    serializer_class = TimetableSlotSerializer
    
    # --- FIX #2: This ordering is correct ---
    ordering = ['start_time']
    ordering_fields = ['start_time']


# --- Email Notification Function ---
# Note: This is a standard function, not an API view.
# To make it accessible via a URL, it needs to be wrapped in an API view.
def send_initial_notification(request):
    # Correctly filter lecturers through the Profile model
    lecturers = User.objects.filter(profile__role='lecturer', is_active=True)
    
    # Create a list of email addresses, ensuring they are not empty
    recipient_list = [lecturer.email for lecturer in lecturers if lecturer.email]

    if recipient_list:
        send_mail(
            subject='Reminder: Please Submit Your FYP Availability',
            message='Dear Lecturers,\n\nPlease log in to the FYPHub to submit your available time slots for the upcoming presentations.\n\nThank you.',
            from_email='your-fyp-system-email@gmail.com', # Use a specific sender email
            recipient_list=recipient_list,
            fail_silently=False,
        )
        # Here you would typically return a success response if this were an API view
        print(f"Successfully sent notifications to {len(recipient_list)} lecturers.")
    else:
        print("No lecturers with valid email addresses found.")