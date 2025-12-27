# --- File: backend/api/urls.py (FINAL & COMPLETE - WITH CSRF FIX) ---

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    UserViewSet,
    FYPProjectViewSet,
    TimetableBookingViewSet,
    TimetableSlotViewSet,
    export_to_google_sheet,
    send_initial_notification,
    get_csrf_token # 1. Import the new view
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserViewSet)
router.register(r'projects', FYPProjectViewSet)
router.register(r'bookings', TimetableBookingViewSet, basename='timetablebooking')
router.register(r'slots', TimetableSlotViewSet, basename='timetableslot')

urlpatterns = [
    path('', include(router.urls)),
    
    # --- 2. Add the new path for our CSRF endpoint ---
    # This creates the endpoint: /api/get-csrf-token/
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
    
    path('export-to-sheet/', export_to_google_sheet, name='export-to-sheet'),
    path('send-notification/', send_initial_notification, name='send-notification'),
]