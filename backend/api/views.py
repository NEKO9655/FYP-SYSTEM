# --- File: backend/api/views.py (FINAL & COMPLETE) ---

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Course, FYPProject, TimetableBooking, TimetableSlot
from .serializers import CourseSerializer, UserSerializer, FYPProjectSerializer, TimetableBookingSerializer, TimetableSlotSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    # Enable filtering by the 'role' field
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profile__role'] # Filter through the related profile model

class FYPProjectViewSet(viewsets.ModelViewSet):
    queryset = FYPProject.objects.all().order_by('student_matric_id')
    serializer_class = FYPProjectSerializer
    
    # Enable filtering capabilities
    filter_backends = [DjangoFilterBackend]
    # --- The CORE FIX is here ---
    # Ensure 'supervisor' is included in the list of filterable fields.
    filterset_fields = ['course', 'fyp_stage', 'supervisor']

class TimetableBookingViewSet(viewsets.ModelViewSet):
    queryset = TimetableBooking.objects.all().order_by('start_time')
    serializer_class = TimetableBookingSerializer

class TimetableSlotViewSet(viewsets.ModelViewSet):
    queryset = TimetableSlot.objects.all().order_by('start_time')
    serializer_class = TimetableSlotSerializer