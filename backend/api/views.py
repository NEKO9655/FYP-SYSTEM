# backend/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Q
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.conf import settings

from .models import Course, Profile, FYPProject, TimetableBooking, TimetableSlot, PresentationDay
from .serializers import (
    CourseSerializer, UserSerializer, FYPProjectSerializer, 
    TimetableBookingSerializer, TimetableSlotSerializer, PresentationDaySerializer
)

# --- 1. CourseViewSet ---
class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role == 'coordinator' and user.profile.course:
            return Course.objects.filter(id=user.profile.course.id)
        return Course.objects.all()

# --- 2. UserViewSet ---
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profile__role']

# --- 3. FYPProjectViewSet ---
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
            queryset = FYPProject.objects.filter(student__profile__course=profile.course) if profile.course else FYPProject.objects.all()
        elif profile.role == 'lecturer':
            queryset = FYPProject.objects.filter(Q(supervisor=user) | Q(co_supervisor=user) | Q(examiner=user)).distinct()
        else:
            queryset = FYPProject.objects.filter(student=user)

        return queryset.order_by('student_matric_id')

# --- 4. TimetableBookingViewSet ---
class TimetableBookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TimetableBookingSerializer

    def get_queryset(self):
        # 让所有人都能看到所有预约，以便前端显示红色的“Occupied”格子
        return TimetableBooking.objects.all().order_by('start_time')

    def perform_create(self, serializer):
        serializer.save(lecturer=self.request.user)

# --- 5. TimetableSlotViewSet ---
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
            queryset = TimetableSlot.objects.filter(project__student__profile__course=profile.course) if profile.course else TimetableSlot.objects.all()
        elif profile.role == 'lecturer':
            queryset = TimetableSlot.objects.filter(Q(project__supervisor=user) | Q(project__co_supervisor=user) | Q(project__examiner=user)).distinct()
        else:
            queryset = TimetableSlot.objects.filter(project__student=user)
            
        return queryset.order_by('start_time')

# --- 6. PresentationDayViewSet (新增：由协调员管理日期) ---
class PresentationDayViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PresentationDaySerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            return PresentationDay.objects.none()
            
        # 协调员和讲师都只能看到所属课程的日期
        if user.profile.course:
            return PresentationDay.objects.filter(course=user.profile.course)
        return PresentationDay.objects.all()

    def perform_create(self, serializer):
        # 自动绑定协调员的课程，增加安全检查
        if hasattr(self.request.user, 'profile') and self.request.user.profile.course:
            serializer.save(course=self.request.user.profile.course)
        else:
            # 如果没分配课程，默认保存但不指定课程（或者你可以根据需求报错）
            serializer.save()

# --- 7. 功能性接口：Google Sheets 导出 ---
@api_view(['POST'])
def export_to_google_sheet(request):
    user = request.user
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
        keyfile_path = os.path.join(settings.BASE_DIR, 'backend', 'client_secret.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open('FYP_Schedule_Sheet').sheet1
        
        slots_queryset = TimetableSlot.objects.all()
        if hasattr(user, 'profile') and user.profile.role == 'coordinator' and user.profile.course:
            slots_queryset = slots_queryset.filter(project__student__profile__course=user.profile.course)
        
        slots = slots_queryset.order_by('start_time')
        header = ['Date', 'Time Slot', 'Venue', 'Student ID', 'Student Name', 'Project Title', 'Supervisor']
        data_to_write = [header]
        
        for slot in slots:
            student_profile = slot.project.student.profile if slot.project and slot.project.student else None
            row = [
                str(slot.start_time.date()),
                f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
                slot.venue,
                slot.project.student_matric_id if slot.project else "N/A",
                student_profile.full_name if student_profile else "N/A",
                slot.project.title if slot.project else 'N/A',
                slot.project.supervisor.profile.full_name if slot.project.supervisor else "N/A"
            ]
            data_to_write.append(row)
        
        sheet.clear()
        sheet.update('A1', data_to_write)
        return Response({'status': 'success', 'url': f"https://docs.google.com/spreadsheets/d/{sheet.spreadsheet.id}"})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

# --- 8. 功能性接口：发送邮件通知 ---
@api_view(['POST'])
def send_initial_notification(request):
    try:
        lecturers = User.objects.filter(profile__role='lecturer', is_active=True)
        recipient_list = [l.email for l in lecturers if l.email]
        if recipient_list:
            send_mail('Reminder: Submit FYP Availability', 'Please book slots in FYPHub.', 'fyp@uts.edu.my', recipient_list)
            return Response({'status': 'success'})
        return Response({'status': 'success', 'message': 'No emails found.'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

# --- 9. 核心：自动化排程算法预留接口 (Phase 2 的天花板) ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_auto_scheduler(request):
    """
    即将在这里编写基于讲师连续性优先的排程算法逻辑。
    目前先返回一个成功消息以供前端测试。
    """
    user = request.user
    if user.profile.role != 'coordinator':
        return Response({'error': 'Unauthorized'}, status=403)
        
    # TODO: 编写自动排程 Python 逻辑
    return Response({'status': 'success', 'message': 'Auto-scheduler logic is being initialized...'})

# --- 10. 获取当前用户信息 ---
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)