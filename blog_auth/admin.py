from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Register your models here.
class EblogUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'is_superuser', 'is_staff', 'date_joined')
    # 默认的user中是有first_name和second_name的，自定义user模型中如果删除了这两个字段，需要排除
    exclude = ('first_name', 'last_name')
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('phone_number',)}),
    # )
    #
    # add_fieldsets =  UserAdmin.add_fieldsets + (
    #
    # )

admin.site.register(User, EblogUserAdmin)
