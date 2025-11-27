from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, FYPProject, TimetableBooking, TimetableSlot

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'get_full_name_from_profile', 'email', 'is_staff')
    
    def get_full_name_from_profile(self, instance):
        return instance.profile.full_name
    get_full_name_from_profile.short_description = 'Full Name'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(FYPProject)
class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor')
    list_filter = ('supervisor', 'examiner')
    # 搜索时，现在通过 profile 的 full_name 字段来搜索
    search_fields = ('title', 'student__username', 'student__profile__full_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner']

admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)