from rest_framework import viewsets
from .models import User, FYPProject, TimetableBooking
from .serializers import UserSerializer, FYPProjectSerializer, TimetableBookingSerializer

# 使用DRF的ModelViewSet，它可以自动为我们处理好增删改查的所有逻辑
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