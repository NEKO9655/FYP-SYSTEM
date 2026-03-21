# --- File: backend/api/urls.py (FINAL & CORRECTED VERSION) ---

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 导入JWT的登录视图
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# 导入我们所有的视图
from .views import (
    CourseViewSet,
    UserViewSet,
    FYPProjectViewSet,
    TimetableBookingViewSet,
    TimetableSlotViewSet,
    CurrentUserView,  # <-- 导入我们刚刚创建的视图
    export_to_google_sheet,
    send_initial_notification
)

# Router的设置保持不变，它工作得很好
router = DefaultRouter()
# 注意：我们为FYPProjectViewSet添加了basename，因为我们自定义了get_queryset
router.register(r'projects', FYPProjectViewSet, basename='project')
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'bookings', TimetableBookingViewSet, basename='timetablebooking')
router.register(r'slots', TimetableSlotViewSet, basename='timetableslot')


urlpatterns = [
    # --- 身份认证的URL ---
    # 1. 登录API (用户用username和password换取access/refresh tokens)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 2. 刷新Token API (用refresh token换取一个新的access token)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 3. 获取当前登录用户信息 API
    path('user/me/', CurrentUserView.as_view(), name='current_user'),

    # --- 你原来的功能性URL ---
    path('export-to-sheet/', export_to_google_sheet, name='export-to-sheet'),
    path('send-notification/', send_initial_notification, name='send-notification'),
    
    # --- 包含所有由Router自动生成的URL ---
    path('', include(router.urls)),
]