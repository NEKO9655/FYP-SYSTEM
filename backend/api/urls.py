from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FYPProjectViewSet, TimetableBookingViewSet, TimetableSlotViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', FYPProjectViewSet)
router.register(r'bookings', TimetableBookingViewSet)
router.register(r'slots', TimetableSlotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]