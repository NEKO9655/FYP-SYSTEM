# backend/backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 告诉Django，所有以 'api/' 开头的URL，都去 'api.urls' 文件里找
    path('api/', include('api.urls')), 
]