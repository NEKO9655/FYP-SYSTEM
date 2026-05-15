# --- File: api/admin.py (最终的、功能最全的整合版) ---
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Programme, Profile, FYPProject, TimetableBooking, 
    TimetableSlot, PresentationDay, Venue,
    Announcements, Feedback, Submissions, 
    MilestoneForms, MilestoneEntries, SupervisorQuotas
)

# --- 1. 创建我们的自定义 Action ---
@admin.action(description='Create placeholder FYP Project for selected students')
def create_placeholder_projects(modeladmin, request, queryset):
    created_count = 0
    # queryset 在这里是 User 对象的列表
    for user in queryset:
        if hasattr(user, 'profile') and user.profile.role == 'student':
            project, created = FYPProject.objects.get_or_create(
                student=user,
                defaults={
                    'title': 'Pending TRF Submission',
                    'student_matric_id': user.profile.student_id_no or user.username,
                    'fyp_stage': 'FYP1',
                    'programme': user.profile.programme
                }
            )
            if created:
                created_count += 1
    modeladmin.message_user(request, f'Successfully created {created_count} new placeholder projects.', 'success')

# --- 2. 整合您的 CustomUserAdmin，并加入 Action ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'get_full_name_from_profile', 'email', 'is_staff', 'get_role_from_profile')
    list_filter = ('profile__role', 'is_staff', 'is_superuser', 'profile__programme') # 建议也按课程筛选
    
    # 【核心新增】: 将我们的新 action 添加到 User 管理界面
    actions = [create_placeholder_projects]

    @admin.display(description='Full Name')
    def get_full_name_from_profile(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.full_name
        return ""

    @admin.display(description='Role')
    def get_role_from_profile(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.role
        return ""

# --- 3. 重新注册 User，使用我们整合后的 Admin 类 ---
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# --- 4. 注册所有其他模型 (保留您优秀的设计) ---

@admin.register(FYPProject)
class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor', 'programme')
    list_filter = ('supervisor', 'examiner', 'programme')
    search_fields = ('title', 'student__username', 'student__profile__full_name')
    # autocomplete_fields 很好，但需要额外配置，我们暂时注释掉以避免错误
    # autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner', 'programme']

# 【核心修正】: 使用 @admin.register 装饰器来注册 Programme
@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

# 使用 @admin.register 注册，代码更整洁
@admin.register(TimetableBooking)
class TimetableBookingAdmin(admin.ModelAdmin):
    list_display = ('project', 'lecturer', 'start_time', 'venue')
    list_filter = ('venue', 'lecturer')

@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ('project', 'start_time', 'venue')

@admin.register(PresentationDay)
class PresentationDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'programme')
    list_filter = ('programme',)

@admin.register(Announcements)
class AnnouncementsAdmin(admin.ModelAdmin):
    list_display = ('title', 'coordinator', 'created_at')

@admin.register(Submissions)
class SubmissionsAdmin(admin.ModelAdmin):
    list_display = ('proposed_project_title', 'student_name', 'status', 'created_at')
    list_filter = ('status', 'programme')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('submission', 'lecturer', 'created_at')

@admin.register(MilestoneForms)
class MilestoneFormsAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'fyp_title', 'lecturer')

# 对于没有特殊配置的模型，可以直接注册
admin.site.register(MilestoneEntries)
admin.site.register(SupervisorQuotas)
admin.site.register(Venue) # 如果没有特殊配置，也可以这样注册