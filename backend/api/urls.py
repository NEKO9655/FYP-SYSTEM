# backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FYPProjectViewSet

# 创建一个路由器，它会自动为我们的ViewSet生成所有URL
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', FYPProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]