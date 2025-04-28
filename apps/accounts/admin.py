from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserRoles

class CustomUserAdmin(UserAdmin):
    # Fields to display in user list
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    
    # Fields in edit view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'profile_picture', 'bio')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields when creating new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

class UserRolesAdmin(admin.ModelAdmin):
    list_display = ('role_id', 'role_name')
    search_fields = ('role_name',)

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserRoles, UserRolesAdmin)