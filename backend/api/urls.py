# --- File: backend/api/urls.py (FINAL & COMPLETE) ---

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, UserViewSet, FYPProjectViewSet, TimetableBookingViewSet, TimetableSlotViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserViewSet)
router.register(r'projects', FYPProjectViewSet)
router.register(r'bookings', TimetableBookingViewSet)
router.register(r'slots', TimetableSlotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]