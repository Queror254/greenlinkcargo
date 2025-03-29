from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

# models : 
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )