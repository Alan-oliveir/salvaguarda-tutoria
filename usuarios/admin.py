# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'tipo', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('tipo',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
