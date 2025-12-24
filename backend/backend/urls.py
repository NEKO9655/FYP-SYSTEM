# --- File: backend/backend/urls.py (FINAL FIXED VERSION) ---

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # The Django admin site
    path('admin/', admin.site.urls),
    
    # All of our application's API endpoints are under /api/
    path('api/', include('api.urls')),
    
    # --- THE CORE FIX IS HERE ---
    # This line enables DRF's built-in login and logout API views.
    # It creates the crucial /api-auth/login/ endpoint that the frontend needs.
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]