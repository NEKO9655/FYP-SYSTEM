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
    PresentationDayViewSet,  # <-- 新增
    CurrentUserView,
    export_to_google_sheet,
    send_initial_notification,
    run_auto_scheduler      # <-- 新增
)

# 1. 使用 Router 处理 ViewSet (自动生成 GET/POST/PUT/DELETE 路由)
router = DefaultRouter()
router.register(r'projects', FYPProjectViewSet, basename='project')
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'bookings', TimetableBookingViewSet, basename='timetablebooking')
router.register(r'slots', TimetableSlotViewSet, basename='timetableslot')
router.register(r'presentation-days', PresentationDayViewSet, basename='presentationday') # <-- 新增

# 2. 定义具体的 URL 路径
urlpatterns = [
    # 身份认证
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/me/', CurrentUserView.as_view(), name='current_user'),

    # 功能性接口 (Function Based Views)
    path('export-to-sheet/', export_to_google_sheet, name='export-to-sheet'),
    path('send-notification/', send_initial_notification, name='send-notification'),
    path('run-scheduler/', run_auto_scheduler, name='run-scheduler'), # <-- 新增自动排程接口

    # 包含 Router 生成的所有路由
    path('', include(router.urls)),
]