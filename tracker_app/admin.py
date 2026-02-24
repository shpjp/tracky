from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'role', 'user', 'status', 'applied_date', 'created_at')
    list_filter = ('status', 'applied_date', 'created_at')
    search_fields = ('company_name', 'role', 'user__username')
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
