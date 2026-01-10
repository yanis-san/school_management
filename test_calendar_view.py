#!/usr/bin/env python
"""
Script pour tester la vue task_calendar
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tasks.views import task_calendar
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()

# Créer une requête factice
rf = RequestFactory()
request = rf.get('/tasks/calendar/?month=2&year=2026')

# Assigner un utilisateur staff
try:
    user = User.objects.filter(is_staff=True).first()
    if not user:
        print("❌ Aucun utilisateur staff trouvé")
        sys.exit(1)
    
    request.user = user
    
    # Appeler la vue
    print("🔍 Test de la vue task_calendar pour février 2026...")
    response = task_calendar(request)
    
    print(f"✅ Vue exécutée avec succès!")
    print(f"   Status Code: {response.status_code}")
    print(f"   Context keys: {list(response.context_data.keys()) if hasattr(response, 'context_data') else 'N/A'}")
    
    if hasattr(response, 'context_data'):
        calendar_weeks = response.context_data.get('calendar_weeks', [])
        print(f"   calendar_weeks length: {len(calendar_weeks)}")
        if calendar_weeks:
            print(f"   First week: {calendar_weeks[0]}")
        else:
            print("   ⚠️ calendar_weeks est vide!")
    
except Exception as e:
    print(f"❌ Erreur lors de l'exécution de la vue:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
