from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Course, Profile, FYPProject, TimetableBooking, 
    TimetableSlot, PresentationDay, Venue,
    Announcements, Feedback, Submissions, 
    MilestoneForms, MilestoneEntries, SupervisorQuotas
)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'get_full_name_from_profile', 'email', 'is_staff', 'get_role_from_profile')
    list_filter = ('profile__role', 'is_staff', 'is_superuser')
    
    @admin.display(description='Full Name')
    def get_full_name_from_profile(self, instance):
        # Added a check to prevent errors if profile does not exist for some reason
        if hasattr(instance, 'profile'):
            return instance.profile.full_name
        return ""

    @admin.display(description='Role')
    def get_role_from_profile(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.role
        return ""

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(FYPProject)
class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor', 'course')
    list_filter = ('supervisor', 'examiner', 'course')
    search_fields = ('title', 'student__username', 'student__profile__full_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner', 'course']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)

@admin.register(PresentationDay)
class PresentationDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'course') # 在列表页显示日期和课程
    list_filter = ('course',)         # 右侧增加按课程筛选

@admin.register(Announcements)
class AnnouncementsAdmin(admin.ModelAdmin):
    list_display = ('title', 'coordinator', 'created_at') # 显示标题、发布人和时间

@admin.register(Submissions)
class SubmissionsAdmin(admin.ModelAdmin):
    list_display = ('proposed_project_title', 'student_name', 'status', 'created_at')
    list_filter = ('status', 'programme') # 侧边栏增加状态筛选

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('submission', 'lecturer', 'created_at')

@admin.register(MilestoneForms)
class MilestoneFormsAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'fyp_title', 'lecturer')

admin.site.register(MilestoneEntries)
admin.site.register(SupervisorQuotas)