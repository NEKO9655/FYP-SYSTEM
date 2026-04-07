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
from datetime import datetime, time, timedelta
from django.utils import timezone # 【新增】处理时区

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
        if not hasattr(user, 'profile'): return FYPProject.objects.none()
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
    # 【修改】添加过滤器后端和筛选字段
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project__fyp_stage'] # 支持按阶段筛选

    def get_queryset(self):
        # 保持之前的逻辑：让所有人看所有预约，以便显示 Occupied
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
        if not hasattr(user, 'profile'): return TimetableSlot.objects.none()
        profile = user.profile
        if profile.role == 'coordinator':
            queryset = TimetableSlot.objects.filter(project__student__profile__course=profile.course) if profile.course else TimetableSlot.objects.all()
        elif profile.role == 'lecturer':
            queryset = TimetableSlot.objects.filter(Q(project__supervisor=user) | Q(project__co_supervisor=user) | Q(project__examiner=user)).distinct()
        else:
            queryset = TimetableSlot.objects.filter(project__student=user)
        return queryset.order_by('start_time')

# --- 6. PresentationDayViewSet ---
class PresentationDayViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PresentationDaySerializer

    def get_queryset(self):
        user = self.request.user
        # 确保 profile 存在且有课程
        if hasattr(user, 'profile') and user.profile.course:
            return PresentationDay.objects.filter(course=user.profile.course)
        return PresentationDay.objects.none()

    def perform_create(self, serializer):
        # 关键修正：确保在保存前明确拿到课程
        user_profile = getattr(self.request.user, 'profile', None)
        
        if user_profile and user_profile.course:
            # 只有这里成功执行，数据库才不会报 Course 缺失
            serializer.save(course=user_profile.course)
        else:
            # 如果走到这里，说明账号虽然是协调员，但 Profile 里的 Course 还是空的
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"course": "Your account is not linked to any course. Please contact Admin."})

# --- 7. Google Sheets 导出 ---
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
            data_to_write.append([
                str(slot.start_time.date()),
                f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
                slot.venue, slot.project.student_matric_id if slot.project else "N/A",
                student_profile.full_name if student_profile else "N/A",
                slot.project.title if slot.project else 'N/A',
                slot.project.supervisor.profile.full_name if slot.project.supervisor else "N/A"
            ])
        sheet.clear()
        sheet.update('A1', data_to_write)
        return Response({'status': 'success', 'url': f"https://docs.google.com/spreadsheets/d/{sheet.spreadsheet.id}"})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

# --- 8. 发送邮件通知 ---
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

# --- 9. 【核心功能】自动化排程算法 ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_auto_scheduler(request):
    user = request.user
    if user.profile.role != 'coordinator' or not user.profile.course:
        return Response({'error': 'Unauthorized or no course assigned'}, status=403)

    course = user.profile.course
    # 1. 查找未排程的项目 (按导师排序有助于连续性分配)
    scheduled_ids = TimetableBooking.objects.values_list('project_id', flat=True)
    unscheduled_projects = FYPProject.objects.filter(
        student__profile__course=course
    ).exclude(id__in=scheduled_ids).order_by('supervisor__username')

    if not unscheduled_projects.exists():
        return Response({'status': 'success', 'message': 'All projects are already scheduled.'})

    pres_days = PresentationDay.objects.filter(course=course).order_by('date')
    venues = ['CL3', 'CL4', 'BLOCK 8, ROOM 801', 'BLOCK 8, ROOM 803']
    project_pool = list(unscheduled_projects)
    created_count = 0

    for day_obj in pres_days:
        for venue in venues:
            last_lecturer_id = None
            # 设定当天起始与结束时间 (转换为有时区的时间)
            curr = timezone.make_aware(datetime.combine(day_obj.date, time(8, 30)))
            end = timezone.make_aware(datetime.combine(day_obj.date, time(17, 0)))

            while curr < end and project_pool:
                # 检查场地是否被占用
                if TimetableBooking.objects.filter(start_time=curr, venue=venue).exists():
                    curr += timedelta(minutes=30)
                    continue

                target = None
                # 策略：优先找与上一场相同的导师或考官，且该老师此刻没有在别的教室开会
                for p in project_pool:
                    # 检查老师冲突：该项目的导师或考官是否正在别的场地报告？
                    busy = TimetableBooking.objects.filter(
                        Q(lecturer_id=p.supervisor_id) | Q(examiner_id=p.supervisor_id) |
                        Q(lecturer_id=p.examiner_id) | Q(examiner_id=p.examiner_id),
                        start_time=curr
                    ).exists()
                    
                    if not busy:
                        if last_lecturer_id in [p.supervisor_id, p.examiner_id]:
                            target = p # 匹配到连续场次
                            break
                
                # 如果没找到连续的，就找第一个不冲突的
                if not target:
                    for p in project_pool:
                        busy = TimetableBooking.objects.filter(
                            Q(lecturer_id=p.supervisor_id) | Q(examiner_id=p.supervisor_id) |
                            Q(lecturer_id=p.examiner_id) | Q(examiner_id=p.examiner_id),
                            start_time=curr
                        ).exists()
                        if not busy:
                            target = p
                            break

                if target:
                    TimetableBooking.objects.create(
                        lecturer=target.supervisor, project=target,
                        examiner=target.examiner, venue=venue,
                        start_time=curr, end_time=curr + timedelta(minutes=30)
                    )
                    last_lecturer_id = target.supervisor_id
                    project_pool.remove(target)
                    created_count += 1
                else:
                    last_lecturer_id = None # 该时段无合适匹配，重置连续性
                
                curr += timedelta(minutes=30)

    return Response({'status': 'success', 'message': f'Scheduled {created_count} projects successfully!'})

# --- 10. 获取当前用户 ---
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)