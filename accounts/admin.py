from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'gender', 'birthday', 'is_staff')
    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_staff', 'gender')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('gender', 'birthday')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
         ),
    )
    ordering = ['email']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number', 'address')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, UserProfileAdmin)
