# --- File: backend/api/admin.py (FINAL REVISED VERSION) ---

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Import all our models
from .models import Profile, FYPProject, TimetableBooking, TimetableSlot

# --- Profile Inline Editor ---
# This class defines how the Profile model will be displayed
# inside the User model's admin page.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False # A user should always have a profile
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

# --- Custom User Admin ---
# We extend the default UserAdmin to include our Profile inline editor.
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    
    # We add 'get_full_name_from_profile' to the list display
    list_display = ('username', 'get_full_name_from_profile', 'email', 'is_staff', 'get_role_from_profile')
    list_filter = ('profile__role', 'is_staff', 'is_superuser') # Filter by role via profile

    # Custom methods to display data from the related Profile model
    def get_full_name_from_profile(self, instance):
        return instance.profile.full_name
    get_full_name_from_profile.short_description = 'Full Name'

    def get_role_from_profile(self, instance):
        return instance.profile.role
    get_role_from_profile.short_description = 'Role'

# --- Unregister the default User admin and register our custom one ---
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# --- FYPProject Admin ---
@admin.register(FYPProject)
class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor')
    list_filter = ('supervisor', 'examiner')
    # Search fields now search through the related profile's full_name
    search_fields = ('title', 'student__username', 'student__profile__full_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner']

# --- Register other models with the default admin interface ---
admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)