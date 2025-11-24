from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FYPProject, LecturerAvailability, TimetableSlot

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor', 'co_supervisor', 'examiner')
    list_filter = ('supervisor', 'examiner')
    search_fields = ('title', 'student__username')

admin.site.register(User, CustomUserAdmin)
admin.site.register(FYPProject, FYPProjectAdmin)
admin.site.register(LecturerAvailability)
admin.site.register(TimetableSlot)