from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Application, CustomUser, RefreshToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'is_email_verified', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('is_email_verified', 'last_login_ip')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name')
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'role', 'user', 'status', 'applied_date', 'created_at')
    list_filter = ('status', 'applied_date', 'created_at')
    search_fields = ('company_name', 'role', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Application Details', {
            'fields': ('company_name', 'role', 'location', 'status')
        }),
        ('Dates', {
            'fields': ('applied_date', 'interview_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'user')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_revoked', 'device_info', 'ip_address')
    list_filter = ('is_revoked', 'created_at', 'expires_at')
    search_fields = ('user__email', 'user__username', 'device_info', 'ip_address')
    readonly_fields = ('token', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'is_revoked', 'created_at', 'expires_at')
        }),
        ('Device Information', {
            'fields': ('device_info', 'ip_address')
        }),
        ('Token Data', {
            'fields': ('token',),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of refresh tokens through admin
        return False
