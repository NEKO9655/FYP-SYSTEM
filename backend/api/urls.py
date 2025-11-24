from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FYPProjectViewSet, TimetableBookingViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', FYPProjectViewSet)
router.register(r'bookings', TimetableBookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]