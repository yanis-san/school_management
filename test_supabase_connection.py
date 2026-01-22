"""
Test Script - Vérifier la connexion Supabase
Exécuter: python test_supabase_connection.py
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from django.conf import settings
from supabase_utils import SupabaseManager

def test_connection():
    """Tester la connexion à la base de données"""
    print("\n" + "="*60)
    print("🧪 TEST DE CONNEXION SUPABASE/DJANGO")
    print("="*60 + "\n")
    
    # 1. Infos DB
    print("📊 Information Base de Données:")
    print("-" * 60)
    db_info = SupabaseManager.get_db_info()
    for key, value in db_info.items():
        print(f"  {key:.<30} {value}")
    print()
    
    # 2. Test Django ORM
    print("🔗 Test Django ORM:")
    print("-" * 60)
    try:
        from django.core.management import call_command
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"  ✅ PostgreSQL Version: {version[0]}")
        print()
    except Exception as e:
        print(f"  ❌ Erreur: {e}\n")
        return False
    
    # 3. Compter les tables
    print("📋 Tables Django:")
    print("-" * 60)
    try:
        from academics.models import Cohort
        from students.models import Student
        from finance.models import Payment
        
        cohorts_count = Cohort.objects.count()
        students_count = Student.objects.count()
        payments_count = Payment.objects.count()
        
        print(f"  📚 Cohorts:    {cohorts_count} enregistrements")
        print(f"  👥 Students:   {students_count} enregistrements")
        print(f"  💰 Payments:   {payments_count} enregistrements")
        print()
    except Exception as e:
        print(f"  ❌ Erreur: {e}\n")
        return False
    
    # 4. Test Supabase Client
    print("🚀 Supabase Client:")
    print("-" * 60)
    try:
        if SupabaseManager.is_using_supabase():
            client = SupabaseManager.get_client()
            if client:
                data = SupabaseManager.select_all('academics_cohort', 'id,name')
                print(f"  ✅ Client Supabase connecté")
                print(f"  📊 Cohorts récupérés: {len(data) if data else 0}")
                if data and len(data) > 0:
                    print(f"  🎯 Exemple: {data[0]['name']}")
                print()
            else:
                print(f"  ⚠️  Supabase Client non configuré\n")
        else:
            print(f"  ℹ️  Supabase non activé (local mode)\n")
    except Exception as e:
        print(f"  ❌ Erreur: {e}\n")
        return False
    
    # 5. Résumé
    print("="*60)
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    print("="*60)
    return True


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
