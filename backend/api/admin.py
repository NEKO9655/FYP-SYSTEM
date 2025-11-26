from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, FYPProject, TimetableBooking, TimetableSlot

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role')


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('username', 'get_full_name', 'email', 'is_staff', 'role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('role', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('role',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'role', 'password', 'password2'),
        }),
    )

    ordering = ('username',)

class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor')
    list_filter = ('supervisor', 'examiner')
    search_fields = ('title', 'student__username', 'student__first_name', 'student__last_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner']

admin.site.register(User, CustomUserAdmin)
admin.site.register(FYPProject, FYPProjectAdmin)
admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)