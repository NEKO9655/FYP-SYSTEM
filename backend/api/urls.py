# --- File: backend/api/urls.py (Phase 2 最终修正版) ---

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# 导入我们所有的视图函数和类
from .views import (
    CourseViewSet,
    UserViewSet,
    FYPProjectViewSet,
    TimetableBookingViewSet,
    TimetableSlotViewSet,
    PresentationDayViewSet,
    CurrentUserView,
    export_to_google_sheet,
    send_initial_notification,
    run_auto_scheduler,
    VenueViewSet,
    SubmissionViewSet,
    MilestoneFormsViewSet,
    ExcelUploadView,
    get_overview_summary
)

# 1. 使用 Router 处理 ViewSet (自动生成 GET/POST/PUT/DELETE 路由)
router = DefaultRouter()
router.register(r'projects', FYPProjectViewSet, basename='project')
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'bookings', TimetableBookingViewSet, basename='timetablebooking')
router.register(r'slots', TimetableSlotViewSet, basename='timetableslot')
router.register(r'presentation-days', PresentationDayViewSet, basename='presentationday')
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'milestones', MilestoneFormsViewSet, basename='milestone')

# 2. 定义具体的 URL 路径
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/me/', CurrentUserView.as_view(), name='current_user'),
    path('export-to-sheet/', export_to_google_sheet, name='export-to-sheet'),
    path('send-notification/', send_initial_notification, name='send-notification'),
    path('run-scheduler/', run_auto_scheduler, name='run-scheduler'),
    path('upload-excel/', ExcelUploadView.as_view(), name='upload-excel'),
    path('overview/summary/', get_overview_summary, name='summary'),

    path('', include(router.urls)),
]