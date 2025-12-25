"""
Script pour synchroniser les prospects convertis avec les étudiants existants.
Marque automatiquement comme 'converted=True' les prospects dont l'email
correspond à un étudiant existant.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from prospects.models import Prospect
from students.models import Student

def sync_converted_prospects():
    """Marque comme convertis les prospects ayant un étudiant correspondant"""
    
    # Récupérer tous les emails des étudiants
    student_emails = set(
        Student.objects.exclude(email__isnull=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )
    
    print(f"Nombre d'étudiants avec email: {len(student_emails)}")
    
    # Trouver les prospects avec email correspondant
    prospects_to_convert = Prospect.objects.filter(
        email__in=student_emails,
        converted=False
    )
    
    count = prospects_to_convert.count()
    print(f"Prospects à marquer comme convertis: {count}")
    
    if count > 0:
        # Afficher les prospects qui seront convertis
        for p in prospects_to_convert[:10]:  # Afficher les 10 premiers
            print(f"  - {p.first_name} {p.last_name} ({p.email})")
        
        if count > 10:
            print(f"  ... et {count - 10} autres")
        
        confirm = input("\nMarquer ces prospects comme convertis? (oui/non): ")
        if confirm.lower() in ['oui', 'o', 'yes', 'y']:
            prospects_to_convert.update(converted=True)
            print(f"✓ {count} prospects marqués comme convertis")
        else:
            print("Annulé")
    else:
        print("Aucun prospect à convertir")

if __name__ == '__main__':
    sync_converted_prospects()
