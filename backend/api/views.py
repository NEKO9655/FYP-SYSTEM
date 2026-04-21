# backend/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta

from .models import (
    Course, Profile, FYPProject, TimetableBooking, 
    TimetableSlot, PresentationDay, Venue, 
    Submissions, Feedback, MilestoneForms, MilestoneEntries, SupervisorQuotas
)
from .serializers import (
    CourseSerializer, UserSerializer, FYPProjectSerializer, 
    TimetableBookingSerializer, TimetableSlotSerializer, PresentationDaySerializer,
    VenueSerializer, 
    SubmissionSerializer, FeedbackSerializer, MilestoneFormsSerializer, MilestoneEntriesSerializer
)

# --- 1. CourseViewSet (保留课程隔离) ---
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

# --- 3. FYPProjectViewSet (保留角色隔离与学号排序) ---
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project__fyp_stage']
    def get_queryset(self):
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
        if hasattr(user, 'profile') and user.profile.course:
            return PresentationDay.objects.filter(course=user.profile.course)
        return PresentationDay.objects.none()
    def perform_create(self, serializer):
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile and user_profile.course:
            serializer.save(course=user_profile.course)
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"course": "Coordinator must have an assigned course."})

class SubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'student':
            return Submissions.objects.filter(student=user)
        elif user.profile.role == 'lecturer':
            return Submissions.objects.filter(supervisor=user)
        return Submissions.objects.all()

    def perform_create(self, serializer):
        # 对应队友 handle_submission 的逻辑
        serializer.save(student=self.request.user, status='submitted')

    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        # 对应队友 submit_feedback 的逻辑
        submission = self.get_object()
        comment = request.data.get('comment')
        new_status = request.data.get('new_status')
        
        # 1. 更新状态
        submission.status = new_status
        submission.save()
        
        # 2. 创建反馈记录
        Feedback.objects.create(
            submission=submission,
            lecturer=request.user,
            comment=comment
        )
        return Response({'success': True})

# --- 9. 【队友功能】Milestones (记事本) ViewSet ---
class MilestoneFormsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MilestoneFormsSerializer

    def get_queryset(self):
        # 只有讲师能看他自己创建的记事本
        return MilestoneForms.objects.filter(lecturer=self.request.user)

    def perform_create(self, serializer):
        form = serializer.save(lecturer=self.request.user)
        # 自动创建 8 个空的里程碑条目 (对应队友 API 3 的初始化逻辑)
        for i in range(1, 9):
            MilestoneEntries.objects.create(form=form, milestone_number=i, status='pending')

# --- 10. 【队友功能】Coordinator 统计逻辑 ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_overview_summary(request):
    # 对应队友的 get_overview_summary
    data = {
        'total_students': User.objects.filter(profile__role='student').count(),
        'total_supervisors': User.objects.filter(profile__role='lecturer').count(),
        'projects_submitted': Submissions.objects.count(),
        'approved_projects': Submissions.objects.filter(status='approved').count(),
        'available_supervisors': 0 # 逻辑可根据 Quota 计算
    }
    return Response({'success': True, 'summary': data})

# --- 7. 功能性接口: Google Sheets 导出 ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_google_sheet(request):
    user = request.user
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
        keyfile_path = os.path.join(settings.BASE_DIR, 'client_secret.json') 
        if not os.path.exists(keyfile_path):
            return Response({'status': 'error', 'message': 'client_secret.json not found'}, status=404)
        creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open('FYP_Schedule_Sheet').sheet1
        bookings_queryset = TimetableBooking.objects.all()
        if hasattr(user, 'profile') and user.profile.role == 'coordinator' and user.profile.course:
            bookings_queryset = bookings_queryset.filter(project__student__profile__course=user.profile.course)
        bookings = bookings_queryset.order_by('start_time')
        header = ['Date', 'Time Slot', 'Venue', 'Student ID', 'Student Name', 'Project Title', 'Supervisor', 'Examiner']
        data_to_write = [header]
        for b in bookings:
            data_to_write.append([
                str(b.start_time.date()),
                f"{b.start_time.strftime('%I:%M %p')} - {b.end_time.strftime('%I:%M %p')}",
                b.venue,
                b.project.student_matric_id if b.project else "N/A",
                b.project.student.profile.full_name if (b.project and b.project.student) else "N/A",
                b.project.title if b.project else "N/A",
                b.lecturer.profile.full_name if b.lecturer else "N/A",
                b.examiner.profile.full_name if b.examiner else "N/A"
            ])
        sheet.clear()
        sheet.update('A1', data_to_write)
        return Response({'status': 'success', 'url': f"https://docs.google.com/spreadsheets/d/{sheet.spreadsheet.id}"})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

# --- 8. 【核心功能】自动化排程算法 ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_auto_scheduler(request):
    user = request.user
    if user.profile.role != 'coordinator' or not user.profile.course:
        return Response({'error': 'Unauthorized or no course assigned'}, status=403)
    course = user.profile.course
    scheduled_ids = TimetableBooking.objects.values_list('project_id', flat=True)
    unscheduled_projects = FYPProject.objects.filter(student__profile__course=course).exclude(id__in=scheduled_ids).order_by('supervisor__username')
    if not unscheduled_projects.exists():
        return Response({'status': 'success', 'message': 'All projects are already scheduled.'})
    pres_days = PresentationDay.objects.filter(course=course).order_by('date')
    venues = ['CL3', 'CL4', 'BLOCK 8, ROOM 801', 'BLOCK 8, ROOM 803']
    project_pool = list(unscheduled_projects)
    created_count = 0
    for day_obj in pres_days:
        for venue in venues:
            last_lecturer_id = None
            curr = timezone.make_aware(datetime.combine(day_obj.date, time(8, 30)))
            end = timezone.make_aware(datetime.combine(day_obj.date, time(17, 0)))
            while curr < end and project_pool:
                if TimetableBooking.objects.filter(start_time=curr, venue=venue).exists():
                    curr += timedelta(minutes=30)
                    continue
                target = None
                for p in project_pool:
                    busy = TimetableBooking.objects.filter(Q(lecturer_id=p.supervisor_id) | Q(examiner_id=p.supervisor_id) | Q(lecturer_id=p.examiner_id) | Q(examiner_id=p.examiner_id), start_time=curr).exists()
                    if not busy and last_lecturer_id in [p.supervisor_id, p.examiner_id]:
                        target = p
                        break
                if not target:
                    for p in project_pool:
                        busy = TimetableBooking.objects.filter(Q(lecturer_id=p.supervisor_id) | Q(examiner_id=p.supervisor_id) | Q(lecturer_id=p.examiner_id) | Q(examiner_id=p.examiner_id), start_time=curr).exists()
                        if not busy:
                            target = p
                            break
                if target:
                    TimetableBooking.objects.create(lecturer=target.supervisor, project=target, examiner=target.examiner, venue=venue, start_time=curr, end_time=curr + timedelta(minutes=30))
                    last_lecturer_id = target.supervisor_id
                    project_pool.remove(target)
                    created_count += 1
                else: last_lecturer_id = None
                curr += timedelta(minutes=30)
    return Response({'status': 'success', 'message': f'Scheduled {created_count} projects successfully!'})

# --- 9. 精准邮件通知功能 ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_initial_notification(request):
    user = request.user
    if user.profile.role != 'coordinator':
        return Response({'error': 'Unauthorized'}, status=403)
    try:
        bookings = TimetableBooking.objects.all()
        if user.profile.course:
            bookings = bookings.filter(project__student__profile__course=user.profile.course)
        lecturer_ids = bookings.values_list('lecturer_id', flat=True)
        examiner_ids = bookings.values_list('examiner_id', flat=True)
        all_relevant_ids = set(list(lecturer_ids) + list(examiner_ids))
        lecturers = User.objects.filter(id__in=all_relevant_ids, is_active=True)
        sent_count = 0
        for lecturer in lecturers:
            if lecturer.email:
                subject = 'FYP Presentation Schedule Ready'
                message = f"Dear {lecturer.profile.full_name or lecturer.username},\n\nYour FYP presentation schedule is ready. Please log in to the portal to view: http://localhost:3000/present-schedule"
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [lecturer.email])
                sent_count += 1
        return Response({'status': 'success', 'message': f'Notified {sent_count} lecturers.'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

# --- 10. 【新增】Excel 数据上传接口 ---
class ExcelUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if request.user.profile.role != 'coordinator':
            return Response({"error": "Only coordinators can upload"}, status=403)
        file_obj = request.FILES.get('file')
        file_type = request.data.get('type') # 'students' 或 'slots'
        if not file_obj: return Response({"error": "No file"}, status=400)
        try:
            df = pd.read_excel(file_obj).replace({np.nan: None})
            if file_type == 'students':
                # 步骤 1: 账号注册
                all_unames = set()
                for col in ['username', 'supervisor_username', 'co_supervisor_username']:
                    if col in df.columns:
                        all_unames.update([str(n).strip() for n in df[col].dropna().unique()])
                for uname in all_unames:
                    user, created = User.objects.get_or_create(username=uname)
                    if created:
                        user.set_password('wow12345')
                        user.save()
                # 步骤 2: Profile & Project
                for _, row in df.iterrows():
                    uname = str(row.get('username', '')).strip()
                    if not uname or uname.lower() == 'none': continue
                    user = User.objects.get(username=uname)
                    course_code = str(row.get('course_code', 'General')).strip()
                    course, _ = Course.objects.get_or_create(code=course_code, defaults={'name': course_code})
                    Profile.objects.update_or_create(user=user, defaults={'full_name': row.get('full_name'), 'role': str(row.get('role', 'student')).lower(), 'course': course})
                    if row.get('project_title'):
                        super_name = str(row.get('supervisor_username', '')).strip()
                        supervisor = User.objects.get(username=super_name) if super_name and super_name.lower() != 'none' else None
                        co_super_name = str(row.get('co_supervisor_username', '')).strip()
                        co_supervisor = User.objects.get(username=co_super_name) if co_super_name and co_super_name.lower() != 'none' else None
                        FYPProject.objects.update_or_create(title=str(row['project_title']).strip(), defaults={'student': user, 'student_matric_id': row.get('student_matric_id'), 'supervisor': supervisor, 'co_supervisor': co_supervisor, 'fyp_stage': row.get('fyp_stage', 'FYP1')})
                return Response({"status": "success", "message": "Students imported!"})
            elif file_type == 'slots':
                for _, row in df.iterrows():
                    project = FYPProject.objects.filter(title=str(row.get('project_title', '')).strip()).first()
                    if project:
                        ex_name = str(row.get('examiner_usernames', '')).strip()
                        if ex_name and ex_name.lower() != 'none':
                            ex_user, _ = User.objects.get_or_create(username=ex_name)
                            Profile.objects.get_or_create(user=ex_user, defaults={'role': 'lecturer'})
                            project.examiner = ex_user
                            project.save()
                return Response({"status": "success", "message": "Examiners updated!"})
        except Exception as e: return Response({"error": str(e)}, status=500)

# --- 11. 当前用户信息 ---
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class VenueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VenueSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.course:
            return Venue.objects.filter(course=user.profile.course)
        return Venue.objects.none()

    def perform_create(self, serializer):
        serializer.save(course=self.request.user.profile.course)