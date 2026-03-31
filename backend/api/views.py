# backend/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Q
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.conf import settings

from .models import Course, Profile, FYPProject, TimetableBooking, TimetableSlot
from .serializers import (
    CourseSerializer, UserSerializer, FYPProjectSerializer, 
    TimetableBookingSerializer, TimetableSlotSerializer
)

# --- 1. CourseViewSet (保留协调员课程隔离) ---
class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role == 'coordinator' and user.profile.course:
            return Course.objects.filter(id=user.profile.course.id)
        return Course.objects.all()

# --- 2. UserViewSet (用于考官下拉列表) ---
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profile__role']

# --- 3. FYPProjectViewSet (保留角色隔离与学号排序) ---
class FYPProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FYPProjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student__profile__course', 'fyp_stage', 'supervisor']

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            return FYPProject.objects.none()

        profile = user.profile

        if profile.role == 'coordinator':
            if profile.course:
                queryset = FYPProject.objects.filter(student__profile__course=profile.course)
            else:
                queryset = FYPProject.objects.all()
        
        elif profile.role == 'lecturer':
            queryset = FYPProject.objects.filter(
                Q(supervisor=user) | Q(co_supervisor=user) | Q(examiner=user)
            ).distinct()

        else:
            queryset = FYPProject.objects.filter(student=user)

        # 核心要求：统一按学号排序
        return queryset.order_by('student_matric_id')

# --- 4. TimetableBookingViewSet (增强：支持双向占用可见) ---
class TimetableBookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TimetableBookingSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            return TimetableBooking.objects.none()

        # 【核心逻辑】：
        # 1. 讲师作为发起人 (Supervisor) 看到的预约
        # 2. 讲师作为被邀请人 (Examiner) 看到的预约
        # 3. 协调员看到全部
        if user.profile.role == 'coordinator':
            return TimetableBooking.objects.all().order_by('start_time')
        
        return TimetableBooking.objects.filter(
            Q(lecturer=user) | Q(examiner=user)
        ).distinct().order_by('start_time')

    def perform_create(self, serializer):
        # 自动将当前登录讲师设为预约发起人
        serializer.save(lecturer=self.request.user)

# --- 5. TimetableSlotViewSet (保留答辩时间表隔离) ---
class TimetableSlotViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TimetableSlotSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project__student__profile__course']

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            return TimetableSlot.objects.none()

        profile = user.profile

        if profile.role == 'coordinator':
            if profile.course:
                queryset = TimetableSlot.objects.filter(project__student__profile__course=profile.course)
            else:
                queryset = TimetableSlot.objects.all()
        
        elif profile.role == 'lecturer':
            queryset = TimetableSlot.objects.filter(
                Q(project__supervisor=user) | 
                Q(project__co_supervisor=user) | 
                Q(project__examiner=user)
            ).distinct()
            
        else:
            queryset = TimetableSlot.objects.filter(project__student=user)
            
        return queryset.order_by('start_time')

# --- 6. Google Sheets 导出功能 (保留全部逻辑) ---
@api_view(['POST'])
def export_to_google_sheet(request):
    user = request.user
    try:
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file", 
            "https://www.googleapis.com/auth/drive"
        ]
        keyfile_path = os.path.join(settings.BASE_DIR, 'backend', 'client_secret.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
        client = gspread.authorize(creds)
        
        sheet_name = 'FYP_Schedule_Sheet'
        sheet = client.open(sheet_name).sheet1
        
        slots_queryset = TimetableSlot.objects.all()

        if hasattr(user, 'profile') and user.profile.role == 'coordinator' and user.profile.course:
            slots_queryset = slots_queryset.filter(project__student__profile__course=user.profile.course)
        
        slots = slots_queryset.order_by('start_time')
        
        header = ['Date', 'Time Slot', 'Venue', 'Student ID', 'Student Name', 'Project Title', 'Supervisor']
        data_to_write = [header]
        
        for slot in slots:
            student_profile = slot.project.student.profile if slot.project and slot.project.student else None
            student_name = student_profile.full_name if student_profile else "N/A"
            student_id = slot.project.student_matric_id if slot.project else "N/A"
            supervisor_name = slot.project.supervisor.profile.full_name if slot.project and slot.project.supervisor else "N/A"

            row = [
                str(slot.start_time.date()),
                f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
                slot.venue,
                student_id,
                student_name,
                slot.project.title if slot.project else 'N/A',
                supervisor_name
            ]
            data_to_write.append(row)
        
        sheet.clear()
        sheet.update('A1', data_to_write)
        
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{sheet.spreadsheet.id}"
        return Response({'status': 'success', 'url': spreadsheet_url})
        
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

# --- 7. 发送邮件通知 (保留) ---
@api_view(['POST'])
def send_initial_notification(request):
    try:
        lecturers = User.objects.filter(profile__role='lecturer', is_active=True)
        recipient_list = [lecturer.email for lecturer in lecturers if lecturer.email]

        if recipient_list:
            send_mail(
                subject='Reminder: Please Submit Your FYP Availability',
                message='Dear Lecturers,\n\nPlease log in to the FYPHub to submit your available time slots.\n\nThank you.',
                from_email='your-fyp-system@uts.edu.my',
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return Response({'status': 'success', 'message': f'Sent to {len(recipient_list)} lecturers.'})
        return Response({'status': 'success', 'message': 'No recipients found.'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

# --- 8. 当前用户信息 (保留) ---
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)