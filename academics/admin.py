# academics/admin.py
from django.contrib import admin
from .models import Subject, Level, Cohort, WeeklySchedule, CourseSession

class WeeklyScheduleInline(admin.TabularInline):
    model = WeeklySchedule
    extra = 1 # Affiche une ligne vide par défaut

class CourseSessionInline(admin.TabularInline):
    model = CourseSession
    fields = ('date', 'start_time', 'end_time', 'status', 'teacher', 'classroom')
    readonly_fields = ('date', 'start_time', 'end_time') # Pour éviter les erreurs manuelles ici
    extra = 0
    show_change_link = True # Permet de cliquer pour modifier une séance spécifique
    can_delete = False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('date')

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'level', 'teacher', 'modality', 'is_individual', 'start_date', 'end_date', 'schedule_generated')
    list_filter = ('academic_year', 'subject', 'level', 'teacher', 'modality', 'is_individual')
    inlines = [WeeklyScheduleInline, CourseSessionInline]
    actions = ['force_schedule_generation']
    
    fieldsets = (
        ('ℹ️ Informations Générales', {
            'fields': ('subject', 'level', 'teacher', 'academic_year')
        }),
        ('📅 Dates & Horaires', {
            'fields': ('start_date', 'end_date', 'schedule', 'max_students')
        }),
        ('🎯 Modalité & Format', {
            'fields': ('modality', 'is_individual'),
            'description': 'Choisissez la modalité (Présentiel/En ligne) et si le groupe est individuel. Le nom s\'adaptera automatiquement.'
        }),
        ('⚙️ Ramadan (Optionnel)', {
            'fields': ('ramadan_start', 'ramadan_end', 'ramadan_start_time', 'ramadan_end_time', 'ramadan_teacher_hourly_rate'),
            'classes': ('collapse',),
        }),
        ('📊 État', {
            'fields': ('schedule_generated',),
            'classes': ('collapse',),
        }),
    )

    def force_schedule_generation(self, request, queryset):
        # Action manuelle au cas où
        for cohort in queryset:
            cohort.schedule_generated = True
            cohort.save()
        self.message_user(request, "Génération du planning lancée.")
    force_schedule_generation.short_description = "Générer les séances pour les groupes sélectionnés"

@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ('date', 'cohort', 'start_time', 'status', 'teacher')
    list_filter = ('status', 'date', 'cohort__teacher')
    date_hierarchy = 'date' # Ajoute une navigation par date en haut
    search_fields = ('cohort__name', 'teacher__username')

admin.site.register(Subject)
admin.site.register(Level)