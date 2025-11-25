from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FYPProject, TimetableBooking, TimetableSlot

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'is_staff', 'role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('role', 'is_staff')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'password2'),
        }),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Custom Fields', {'fields': ('role',)}),
    )
    
class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor')
    list_filter = ('supervisor', 'examiner')
    
    search_fields = ('title', 'student__username', 'student__first_name', 'student__last_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner']

admin.site.register(User, CustomUserAdmin)
admin.site.register(FYPProject, FYPProjectAdmin)
admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)