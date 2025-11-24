from rest_framework import viewsets
from .models import User, FYPProject, TimetableBooking, TimetableSlot
from .serializers import UserSerializer, FYPProjectSerializer, TimetableBookingSerializer, TimetableSlotSerializer

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