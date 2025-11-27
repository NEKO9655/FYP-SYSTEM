# backend/api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User, FYPProject, TimetableBooking, TimetableSlot
# --- 1. 我们不再需要 UserCreationForm，因为我们将直接在Admin类中定义字段 ---

# --- 2. 我们只需要一个用于“编辑”的表单，并确保它不包含 first_name/last_name ---
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        # 只包含我们模型中实际存在的字段
        fields = ('username', 'email', 'full_name', 'role')

# --- 3. 重新定义 CustomUserAdmin，这是最关键的部分 ---
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # 'fieldsets' 是【编辑】和【添加】页面共同的布局
    # 我们彻底重写它，只使用 full_name
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("full_name", "email")}),
        (_("Custom Fields"), {"fields": ("role",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    
    # 'add_fieldsets' 在这种简化模式下可以不需要，但保留以防万一
    # 我们在这里也只使用 full_name
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'email', 'role', 'password', 'password2'),
        }),
    )

    # 'list_display' 是用户列表页显示的列
    list_display = ("username", "full_name", "email", "is_staff", "role")
    # 让后台可以通过 full_name 来搜索用户
    search_fields = ("username", "full_name", "email")
    list_filter = ("role", "is_staff", "is_superuser")
    ordering = ("username",)

# --- FYPProjectAdmin 和其他注册保持不变 ---
@admin.register(FYPProject)
class FYPProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'supervisor')
    list_filter = ('supervisor', 'examiner')
    search_fields = ('title', 'student__username', 'student__full_name')
    autocomplete_fields = ['student', 'supervisor', 'co_supervisor', 'examiner']

# --- 其他模型使用默认注册即可 ---
admin.site.register(TimetableBooking)
admin.site.register(TimetableSlot)