from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    FYPProjectViewSet,
    TimetableBookingViewSet,
    TimetableSlotViewSet,
    export_to_google_sheet,
    send_initial_notification
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', FYPProjectViewSet)
router.register(r'bookings', TimetableBookingViewSet)
router.register(r'slots', TimetableSlotViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('export-to-sheet/', export_to_google_sheet, name='export-to-sheet'),
    path('send-notification/', send_initial_notification, name='send-notification'),
]