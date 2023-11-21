from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_staff', 'fullname')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_staff', 'gender', 'fullname')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('profile_picture', 'fullname', 'gender', 'birthday')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password')}
         ),
    )
    ordering = ['email']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__email', 'phone_number', 'address')


admin.site.register(User, UserAdmin)
admin.site.register(Profile, UserProfileAdmin)
