# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AcademicYear, Classroom

class CustomUserAdmin(UserAdmin):
    # On ajoute nos champs personnalisés à l'interface User existante
    fieldsets = UserAdmin.fieldsets + (
        ('Rôles École', {'fields': ('is_teacher', 'is_admin', 'phone')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_teacher', 'is_staff')
    list_filter = ('is_teacher', 'is_staff')

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('label', 'start_date', 'end_date', 'is_current')
    list_editable = ('is_current',) # Pour changer l'année active rapidement

admin.site.register(User, CustomUserAdmin)
admin.site.register(Classroom)