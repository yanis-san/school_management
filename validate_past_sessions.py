#!/usr/bin/env python
"""
Script pour valider automatiquement toutes les séances passées non validées.
Peut être relancé plusieurs fois sans problème (ignore les séances déjà validées).

Usage:
    python validate_past_sessions.py
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from academics.models import CourseSession, Cohort

def validate_past_sessions():
    """Valide toutes les séances passées qui ne sont pas encore validées."""
    
    today = date.today()
    
    # Trouver toutes les séances passées non validées (exclure les reportées)
    past_sessions = CourseSession.objects.filter(
        date__lt=today,
        status='SCHEDULED'  # Seulement celles qui ne sont pas encore validées
    ).exclude(
        status='POSTPONED'  # Ignorer les séances reportées
    ).select_related('cohort').order_by('cohort__name', 'date')
    
    total = past_sessions.count()
    
    if total == 0:
        print("✓ Aucune séance passée à valider. Tout est à jour!")
        return
    
    print(f"\n📋 Trouvé {total} séance(s) passée(s) à valider\n")
    
    # Grouper par cohort pour l'affichage
    cohort_counts = {}
    for session in past_sessions:
        cohort_name = session.cohort.name
        if cohort_name not in cohort_counts:
            cohort_counts[cohort_name] = []
        cohort_counts[cohort_name].append(session.date.strftime('%d/%m/%Y'))
    
    # Afficher le résumé
    for cohort_name, dates in cohort_counts.items():
        print(f"  • {cohort_name}: {len(dates)} séance(s)")
        for date_str in dates[:5]:  # Afficher max 5 dates
            print(f"    - {date_str}")
        if len(dates) > 5:
            print(f"    ... et {len(dates) - 5} autre(s)")
    
    # Demander confirmation
    print(f"\n⚠️  Ces {total} séance(s) vont être marquées comme COMPLETED")
    print("   Les étudiants ne seront PAS marqués absents.")
    print("   Les profs seront payés pour ces heures.\n")
    
    response = input("Continuer? (oui/non): ").strip().lower()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("\n❌ Annulé. Aucune modification effectuée.")
        return
    
    # Valider toutes les séances
    updated = past_sessions.update(status='COMPLETED')
    
    print(f"\n✅ {updated} séance(s) validée(s) avec succès!")
    print("   Vous pouvez relancer ce script à tout moment.\n")


if __name__ == '__main__':
    try:
        validate_past_sessions()
    except KeyboardInterrupt:
        print("\n\n❌ Annulé par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
