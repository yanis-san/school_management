from django.contrib import admin
from .models import Prospect


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'activity_type', 'converted', 'created_at')
    list_filter = ('converted', 'source', 'activity_type', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'age', 'birth_date')
        }),
        ('Intérêts', {
            'fields': ('activity_type', 'specific_course', 'source', 'level')
        }),
        ('Message & Notes', {
            'fields': ('message', 'notes')
        }),
        ('Conversion', {
            'fields': ('converted',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
