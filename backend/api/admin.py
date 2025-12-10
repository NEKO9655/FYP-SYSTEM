# --- File: backend/api/admin.py (FINAL INTEGRATED VERSION) ---

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# --- 1. Import the new 'Course' model ---
from .models import Course, Profile, FYPProject, TimetableBooking, TimetableSlot

# --- Profile Inline Editor (remains unchanged) ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

# --- Custom User Admin (remains unchanged) ---
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'get_full_name_from_profile', 'email', 'is_staff', 'get_role_from_profile')
    list_filter = ('profile__role', 'is_staff', 'is_superuser')

    def get_full_name_from_profile(self, instance):
        return instance.profile.full_name
    get_full_name_from_profile.short_description = 'Full Name'

    def get_role_from_profile(self, instance):
        return instance.profile.role
    get_role_from_profile.short_description = 'Role'

# --- Unregister/Register User (remains unchanged) ---
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# --- FYPProject Admin (remains unchanged) ---
@admin.register(FYPProject)
class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor', 'course') # Added 'course' to the display
    list_filter = ('supervisor', 'examiner', 'course') # Added 'course' to the filter options
    search_fields = ('title', 'student__username', 'student__profile__full_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner']
    
    # It's good practice to also make ForeignKey fields searchable
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner', 'course']

# --- 2. Register the 'Course' model and other models ---
# By registering Course, it will appear in the admin sidebar.
admin.site.register(Course)
admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)