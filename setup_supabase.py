#!/usr/bin/env python
"""
Setup Script - Configuration Supabase pour Django
Exécuter: python setup_supabase.py
"""

import os
import sys
from pathlib import Path

def setup_supabase():
    """Configuration interactive de Supabase"""
    
    print("\n" + "="*70)
    print("🚀 CONFIGURATION SUPABASE POUR DJANGO")
    print("="*70 + "\n")
    
    print("📋 Récupérez vos identifiants sur: https://app.supabase.com/")
    print("   Settings → Database → Connection Info\n")
    
    # Créer/modifier .env
    env_path = Path(__file__).parent / '.env'
    
    print("❓ Voulez-vous configurer Supabase maintenant? (y/n)")
    choice = input(">>> ").strip().lower()
    
    if choice != 'y':
        print("\n✅ Configuration ignorée. Utilisez le fichier .env pour configurer plus tard.\n")
        return
    
    # Recueillir les identifiants
    print("\n" + "-"*70)
    print("📝 ENTREZ VOS IDENTIFIANTS SUPABASE")
    print("-"*70 + "\n")
    
    print("Méthode 1: Connection String (plus simple)")
    print("Format: postgresql://postgres:PASSWORD@HOST:5432/postgres\n")
    
    db_url = input("Connection String (appuyez sur Entrée pour passer): ").strip()
    
    if not db_url:
        print("\nMéthode 2: Variables individuelles\n")
        db_host = input("Host (ex: myproject.supabase.co): ").strip()
        db_user = input("User (ex: postgres): ").strip()
        db_password = input("Password: ").strip()
        db_name = input("Database name (ex: postgres): ").strip() or "postgres"
    else:
        db_host = ""
        db_user = ""
        db_password = ""
        db_name = ""
    
    print("\n" + "-"*70)
    print("🔑 IDENTIFIANTS API (optionnel pour non-ORM)")
    print("-"*70 + "\n")
    
    supabase_url = input("Supabase URL (ex: https://xxx.supabase.co): ").strip()
    supabase_key = input("Supabase Anon Key: ").strip()
    
    # Générer le contenu .env
    env_content = f"""# =====================================================
# CONFIGURATION SUPABASE
# =====================================================

# 🔄 SÉLECTION BASE DE DONNÉES
USE_SUPABASE=true

"""
    
    if db_url:
        env_content += f"""# 📍 Connection String
SUPABASE_DB_URL={db_url}

"""
    else:
        env_content += f"""# 📍 Variables individuelles
SUPABASE_DB_NAME={db_name}
SUPABASE_DB_USER={db_user}
SUPABASE_DB_PASSWORD={db_password}
SUPABASE_DB_HOST={db_host}
SUPABASE_DB_PORT=5432

"""
    
    env_content += f"""# 🔑 API Keys
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# =====================================================
# 📦 DJANGO SETTINGS
# =====================================================
SECRET_KEY=django-insecure-$g*3j_mhpm*0uf^rt+)g8eh&2cxp2dh75+94^)c$_+#3lh%7dx
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
"""
    
    # Sauvegarder
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("\n" + "="*70)
    print("✅ Configuration sauvegardée dans .env")
    print("="*70)
    
    print("\n📋 Prochaines étapes:")
    print("  1. Testez la connexion:")
    print("     python test_supabase_connection.py")
    print("  2. Lancez les migrations:")
    print("     python manage.py migrate")
    print("  3. Démarrez le serveur:")
    print("     python manage.py runserver\n")


if __name__ == '__main__':
    try:
        setup_supabase()
    except KeyboardInterrupt:
        print("\n\n❌ Configuration annulée.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        sys.exit(1)
