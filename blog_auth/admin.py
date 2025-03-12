from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Register your models here.
class EblogUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'is_superuser', 'is_staff', 'date_joined')

    # 排除 first_name 和 last_name 字段
    exclude = ('first_name', 'last_name')

    # 自定义字段集，不包括 first_name 和 last_name
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('profile', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Personal info', {'fields': ('profile', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

admin.site.register(User, EblogUserAdmin)