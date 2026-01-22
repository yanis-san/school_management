"""
Exemple d'intégration de get_abbreviation() dans l'admin Django.
Ajoutez ce code à: academics/admin.py
"""

from django.contrib import admin
from academics.models import Subject, Level, Cohort, WeeklySchedule, CourseSession

# ============================================================================
# ADMIN POUR LES COHORTS AVEC ABRÉVIATION
# ============================================================================

class WeeklyScheduleInline(admin.TabularInline):
    model = WeeklySchedule
    extra = 1

class CourseSessionInline(admin.TabularInline):
    model = CourseSession
    extra = 0
    readonly_fields = ['date', 'start_time', 'end_time', 'status']


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    """Admin pour les Cohorts avec abréviation affichée."""
    
    list_display = [
        'name',
        'get_abbreviation_display',  # Affiche l'abréviation
        'subject',
        'level',
        'modality_display',
        'teacher',
        'start_date',
        'sessions_count',
    ]
    
    list_filter = [
        'subject',
        'level',
        'modality',
        'is_individual',
        'start_date',
    ]
    
    search_fields = [
        'name',
        'subject__name',
        'level__name',
    ]
    
    readonly_fields = [
        'name',  # Généré automatiquement
        'abbreviation_info',  # Affichage de l'abréviation
        'sessions_info',
    ]
    
    inlines = [WeeklyScheduleInline, CourseSessionInline]
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('name', 'abbreviation_info', 'subject', 'level')
        }),
        ('Dates', {
            'fields': ('academic_year', 'start_date', 'end_date')
        }),
        ('Enseignants', {
            'fields': ('teacher', 'substitute_teacher', 'substitute_teachers', 'teacher_hourly_rate')
        }),
        ('Modalité', {
            'fields': ('modality', 'is_individual')
        }),
        ('Ramadan', {
            'fields': (
                'ramadan_start', 'ramadan_end',
                'ramadan_start_time', 'ramadan_end_time',
                'ramadan_teacher_hourly_rate'
            ),
            'classes': ('collapse',)  # Section repliable
        }),
        ('Tarification', {
            'fields': ('standard_price',)
        }),
        ('Génération de Séances', {
            'fields': ('schedule_generated',),
            'description': 'Cochez pour générer automatiquement les séances selon le planning'
        }),
        ('Statistiques', {
            'fields': ('sessions_info',),
            'classes': ('collapse',)
        }),
    )
    
    # ========================================================================
    # MÉTHODES PERSONNALISÉES POUR L'AFFICHAGE
    # ========================================================================
    
    def get_abbreviation_display(self, obj):
        """Affiche l'abréviation dans la liste."""
        abbr = obj.get_abbreviation()
        return f"🏷️ {abbr}"
    
    get_abbreviation_display.short_description = "Abréviation"
    
    def abbreviation_info(self, obj):
        """Affiche l'abréviation dans les détails avec explications."""
        abbr = obj.get_abbreviation()
        
        # Extraire les composants
        subject_code = ""
        level_code = ""
        modality_code = ""
        date_code = ""
        
        # Essayer de parser
        if len(abbr) >= 4:
            # Chercher où finit le code langue
            for i in range(1, min(6, len(abbr))):
                if abbr[i].isdigit():
                    subject_code = abbr[:i]
                    rest = abbr[i:]
                    
                    # Chercher les chiffres du niveau
                    j = 0
                    while j < len(rest) and rest[j].isdigit():
                        j += 1
                    level_code = rest[:j]
                    rest = rest[j:]
                    
                    # Modalité et date
                    if len(rest) >= 2:
                        # Les 4 derniers caractères sont la date
                        date_code = rest[-4:]
                        modality_code = rest[:-4]
                    break
        
        modality_text = {
            'P': '📍 Présentiel',
            'O': '🌐 Online',
            'IP': '👤📍 Individuel Présentiel',
            'IO': '👤🌐 Individuel Online',
        }.get(modality_code, '?')
        
        html = f"""
        <div style="font-family: monospace; background: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 5px;">
            <strong style="font-size: 16px;">{abbr}</strong><br><br>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #e8f4f8;">
                    <td style="padding: 5px; border: 1px solid #ccc;"><strong>Code Langue</strong></td>
                    <td style="padding: 5px; border: 1px solid #ccc;"><code>{subject_code}</code> = {obj.subject.name}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border: 1px solid #ccc;"><strong>Niveau</strong></td>
                    <td style="padding: 5px; border: 1px solid #ccc;"><code>{level_code}</code> = {obj.level.name}</td>
                </tr>
                <tr style="background: #e8f4f8;">
                    <td style="padding: 5px; border: 1px solid #ccc;"><strong>Modalité</strong></td>
                    <td style="padding: 5px; border: 1px solid #ccc;"><code>{modality_code}</code> = {modality_text}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border: 1px solid #ccc;"><strong>Date</strong></td>
                    <td style="padding: 5px; border: 1px solid #ccc;"><code>{date_code}</code> = {obj.start_date.strftime('%B %Y')}</td>
                </tr>
            </table>
        </div>
        """
        return admin.utils.mark_safe(html)
    
    abbreviation_info.short_description = "🔍 Abréviation Détaillée"
    
    def modality_display(self, obj):
        """Affiche la modalité avec emoji."""
        modality_map = {
            'ONLINE': '🌐 En ligne',
            'IN_PERSON': '📍 Présentiel',
        }
        individual_text = '👤 ' if obj.is_individual else ''
        return f"{individual_text}{modality_map.get(obj.modality, '?')}"
    
    modality_display.short_description = "Modalité"
    
    def sessions_count(self, obj):
        """Affiche le nombre de séances avec breakdown."""
        completed = obj.completed_sessions_count
        remaining = obj.remaining_sessions_count
        total = obj.sessions.count()
        
        if total == 0:
            return "Aucune séance"
        
        return f"✅ {completed}/{total} complétées | ⏳ {remaining} en attente"
    
    sessions_count.short_description = "Séances"
    
    def sessions_info(self, obj):
        """Affiche les détails des séances."""
        
        statuses = {
            'SCHEDULED': ('📅 Planifiée', 'blue'),
            'COMPLETED': ('✅ Complétée', 'green'),
            'CANCELLED': ('❌ Annulée', 'red'),
            'POSTPONED': ('⏸️ Reportée', 'orange'),
        }
        
        counts = {}
        for status_key, (display_text, color) in statuses.items():
            count = obj.sessions.filter(status=status_key).count()
            counts[status_key] = (display_text, color, count)
        
        html = f"""
        <div style="background: #f9f9f9; padding: 10px; border-radius: 5px;">
            <strong>Total de séances: {obj.sessions.count()}</strong><br><br>
            <table style="width: 100%; border-collapse: collapse;">
        """
        
        for status_key, (display_text, color, count) in counts.items():
            html += f"""
                <tr>
                    <td style="padding: 5px; border: 1px solid #ddd; background: #{color}22;">
                        {display_text}: <strong>{count}</strong>
                    </td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return admin.utils.mark_safe(html)
    
    sessions_info.short_description = "📊 Résumé des Séances"


# Enregistrer les autres modèles aussi

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# ============================================================================
# OPTIONAL: ACTION PERSONNALISÉE
# ============================================================================

def export_abbreviations(modeladmin, request, queryset):
    """Action pour exporter les abréviations sélectionnées."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cohorts_abbreviations.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom du Cohort', 'Abréviation', 'Sujet', 'Niveau', 'Modalité'])
    
    for cohort in queryset:
        writer.writerow([
            cohort.name,
            cohort.get_abbreviation(),
            cohort.subject.name,
            cohort.level.name,
            cohort.get_modality_display(),
        ])
    
    return response

export_abbreviations.short_description = "📥 Exporter les abréviations (CSV)"


# Ajouter l'action au CohortAdmin
CohortAdmin.actions = [export_abbreviations]


# ============================================================================
# INSTRUCTIONS D'INTÉGRATION
# ============================================================================

"""
POUR INTÉGRER CET ADMIN PERSONNALISÉ:

1. Ouvrir: academics/admin.py

2. Remplacer la classe CohortAdmin existante par le code ci-dessus

3. Tester en allant sur:
   http://localhost:8000/admin/academics/cohort/
   
4. Les nouveautés visibles:
   - Colonne "Abréviation" dans la liste
   - Section "Abréviation Détaillée" avec breakdown
   - Action pour exporter les abréviations en CSV
   - Affichage amélioré des modalités et séances

5. (Optionnel) Ajouter à la liste de recherche:
   search_fields = [
       'name',
       'subject__name',
       'level__name',
       # Pour chercher par abréviation (nécessite une recherche en Python)
   ]
"""
