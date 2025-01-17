from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Register your models here.
class EblogUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'is_superuser', 'is_staff', 'date_joined')
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('phone_number',)}),
    # )
    #
    # add_fieldsets =  UserAdmin.add_fieldsets + (
    #
    # )

admin.site.register(User, EblogUserAdmin)
