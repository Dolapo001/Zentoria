# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'gender', 'birthday', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'gender')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('gender', 'birthday')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
         ),
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'profile_picture', 'phone_number')
    search_fields = ('user__username', 'fullname', 'phone_number')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, UserProfileAdmin)
