# --- File: backend/api/admin.py (FINAL FIXED VERSION) ---

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
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
    list_display = ('title', 'student', 'supervisor', 'course')
    list_filter = ('supervisor', 'examiner', 'course')
    search_fields = ('title', 'student__username', 'student__profile__full_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner', 'course']

# --- 【NEW】Course Admin ---
# This class is necessary for autocomplete_fields to work on the Course model.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name') # This tells Django how to search for courses

# --- Register other models ---
admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)