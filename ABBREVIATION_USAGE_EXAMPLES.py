"""
Exemples d'utilisation de la méthode get_abbreviation() dans une application Django.
Ces exemples montrent comment intégrer l'abréviation dans différents contextes.
"""

# ============================================================================
# 1. UTILISATION BASIQUE
# ============================================================================

from academics.models import Cohort

# Récupérer un cohort
cohort = Cohort.objects.first()

# Obtenir l'abréviation
abbreviation = cohort.get_abbreviation()
print(f"Abréviation: {abbreviation}")


# ============================================================================
# 2. EN TEMPLATE DJANGO
# ============================================================================

"""
Dans un fichier HTML/template Django:

{% for cohort in cohorts %}
<tr>
    <td>{{ cohort.name }}</td>
    <td>{{ cohort.get_abbreviation }}</td>
    <td>
        <!-- Utiliser l'abréviation pour créer un ID unique -->
        <a href="/cohort/{{ cohort.get_abbreviation }}/">Voir détails</a>
    </td>
</tr>
{% endfor %}
"""


# ============================================================================
# 3. EXPORT CSV AVEC ABRÉVIATION
# ============================================================================

import csv
from io import StringIO
from django.http import HttpResponse

def export_cohorts_csv(request):
    """Exporte les cohorts avec leurs abréviations."""
    
    cohorts = Cohort.objects.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cohorts_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom', 'Abréviation', 'Sujet', 'Niveau', 'Modalité'])
    
    for cohort in cohorts:
        writer.writerow([
            cohort.id,
            cohort.name,
            cohort.get_abbreviation(),
            cohort.subject.name,
            cohort.level.name,
            cohort.get_modality_display(),
        ])
    
    return response


# ============================================================================
# 4. UTILISER L'ABRÉVIATION COMME CLÉ DE CACHE
# ============================================================================

from django.core.cache import cache

def get_cohort_stats(cohort_id):
    """Récupère les stats du cohort en utilisant l'abréviation comme clé de cache."""
    
    cohort = Cohort.objects.get(id=cohort_id)
    cache_key = f"cohort_stats_{cohort.get_abbreviation()}"
    
    # Essayer récupérer du cache
    stats = cache.get(cache_key)
    if stats is not None:
        return stats
    
    # Sinon, calculer et mettre en cache
    stats = {
        'total_sessions': cohort.sessions.count(),
        'completed_sessions': cohort.completed_sessions_count,
        'remaining_sessions': cohort.remaining_sessions_count,
    }
    
    # Mettre en cache pour 1 heure
    cache.set(cache_key, stats, 3600)
    return stats


# ============================================================================
# 5. NOMMER DES FICHIERS EXPORT/RAPPORT
# ============================================================================

from datetime import datetime

def generate_attendance_report(cohort):
    """Génère un nom de fichier avec l'abréviation."""
    
    abbr = cohort.get_abbreviation()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"Attendance_{abbr}_{timestamp}.pdf"
    
    return filename

# Exemple:
# Attendance_JPN6IO0126_20260122_143025.pdf


# ============================================================================
# 6. LOGUER AVEC L'ABRÉVIATION POUR MEILLEURE TRAÇABILITÉ
# ============================================================================

import logging

logger = logging.getLogger(__name__)

def create_session(cohort, date, start_time):
    """Crée une séance en loguant avec l'abréviation."""
    
    abbr = cohort.get_abbreviation()
    
    logger.info(f"Creating session for cohort {abbr} on {date} at {start_time}")
    
    try:
        # Logique de création
        session = cohort.sessions.create(date=date, start_time=start_time)
        logger.info(f"Session created successfully: {abbr} - {session.id}")
        return session
    except Exception as e:
        logger.error(f"Failed to create session for {abbr}: {str(e)}")
        raise


# ============================================================================
# 7. UTILISER L'ABRÉVIATION POUR GROUPER/ANALYSER
# ============================================================================

from django.db.models import Count, Q

def get_cohorts_by_abbreviation_prefix(prefix):
    """Récupère tous les cohorts d'une langue spécifique."""
    # Exemple: "JPN" pour tous les cohorts Japonais
    
    all_cohorts = Cohort.objects.all()
    matching = [c for c in all_cohorts if c.get_abbreviation().startswith(prefix)]
    
    return matching


# ============================================================================
# 8. CRÉER UN IDENTIFIANT UNIQUE POUR L'API
# ============================================================================

from rest_framework import viewsets
from rest_framework.response import Response

class CohortViewSet(viewsets.ViewSet):
    """API REST utilisant l'abréviation comme slug unique."""
    
    def retrieve(self, request, pk=None):
        """
        /api/cohorts/CHN3P0126/
        """
        try:
            # pk est l'abréviation
            cohort = [c for c in Cohort.objects.all() if c.get_abbreviation() == pk]
            if cohort:
                cohort = cohort[0]
                return Response({
                    'id': cohort.id,
                    'name': cohort.name,
                    'abbreviation': cohort.get_abbreviation(),
                    'subject': cohort.subject.name,
                    'level': cohort.level.name,
                })
        except Exception as e:
            return Response({'error': str(e)}, status=400)


# ============================================================================
# 9. UTILISER EN QUERYSET (Annotation personnalisée)
# ============================================================================

from django.db.models import F, Value

def get_cohorts_with_abbr():
    """Récupère les cohorts avec abréviation."""
    
    cohorts = Cohort.objects.all().values(
        'id',
        'name',
        'subject__name',
        'level__name',
    )
    
    # Ajouter manuellement l'abréviation (nécessite une boucle)
    for cohort in cohorts:
        cohort_obj = Cohort.objects.get(id=cohort['id'])
        cohort['abbreviation'] = cohort_obj.get_abbreviation()
    
    return cohorts


# ============================================================================
# 10. DASHBOARD/STATISTIQUES PAR ABRÉVIATION
# ============================================================================

def get_dashboard_data():
    """Crée un dashboard avec les cohorts groupés par abréviation."""
    
    dashboard = {}
    
    for cohort in Cohort.objects.all():
        abbr = cohort.get_abbreviation()
        
        if abbr not in dashboard:
            dashboard[abbr] = {
                'cohort': cohort,
                'sessions_count': 0,
                'completed': 0,
                'pending': 0,
            }
        
        # Mettre à jour les statistiques
        dashboard[abbr]['sessions_count'] = cohort.sessions.count()
        dashboard[abbr]['completed'] = cohort.completed_sessions_count
        dashboard[abbr]['pending'] = cohort.remaining_sessions_count
    
    return dashboard


# ============================================================================
# RÉSUMÉ DES CAS D'USAGE
# ============================================================================

"""
✅ MEILLEURS CAS D'USAGE POUR get_abbreviation():

1. 📋 Rapports et Exports
   - Noms de fichiers: f"Rapporte_{abbr}.pdf"
   - En-têtes CSV/Excel
   - Identifiants dans les bases de données externes

2. 🔍 Recherche et Filtrage
   - Rechercher par cohort via URL: /cohort/CHN3P0126/
   - Filtrer dans des formulaires
   - Tags et classifications

3. 📊 Analytics et Dashboards
   - Grouper les données par abréviation
   - Créer des rapports comparatifs
   - Visualisations par langue/niveau

4. 📝 Logs et Traçabilité
   - Identifier rapidement les cohorts dans les logs
   - Audits
   - Messages d'erreur descriptifs

5. 💾 Cache et Performance
   - Utiliser comme clé de cache
   - Identifier les données mises en cache
   - Gestion des sessions

6. 🌐 API REST
   - Slugs d'URL
   - Identifiants dans les réponses JSON
   - Paramètres de requête

7. 📱 Notifications
   - Messages court et lisible
   - SMS/Email avec identifiant
   - Alertes système
"""
