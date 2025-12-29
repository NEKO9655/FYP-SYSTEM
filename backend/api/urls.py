# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    UserViewSet,
    FYPProjectViewSet,
    TimetableBookingViewSet,
    TimetableSlotViewSet,
    export_to_google_sheet,
    send_initial_notification
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserViewSet)
router.register(r'projects', FYPProjectViewSet)
router.register(r'bookings', TimetableBookingViewSet, basename='timetablebooking')

# --- 【核心修复在这里】 ---
# Because TimetableSlotViewSet uses a dynamic get_queryset() method,
# we must explicitly provide a 'basename' for the router.
router.register(r'slots', TimetableSlotViewSet, basename='timetableslot')

urlpatterns = [
    path('', include(router.urls)),
    path('export-to-sheet/', export_to_google_sheet, name='export-to-sheet'),
    path('send-notification/', send_initial_notification, name='send-notification'),
]