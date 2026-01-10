#!/usr/bin/env python
"""
Script pour créer et appliquer les migrations pour l'app tasks
"""
import os
import sys
import subprocess
from pathlib import Path

# Déterminer le chemin du projet
PROJECT_DIR = Path(__file__).resolve().parent

# Chemin vers le venv
VENV_PYTHON = PROJECT_DIR / '.venv' / 'Scripts' / 'python.exe'

def run_command(cmd):
    """Exécuter une commande et afficher la sortie"""
    print(f"Exécution: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

if __name__ == '__main__':
    os.chdir(PROJECT_DIR)
    
    print("=" * 60)
    print("CRÉATION DES MIGRATIONS POUR TASKS")
    print("=" * 60)
    
    # Créer les migrations
    print("\n1. Création de la migration...")
    ret = run_command([str(VENV_PYTHON), 'manage.py', 'makemigrations', 'tasks'])
    
    if ret == 0:
        print("\n✅ Migration créée avec succès!")
        
        # Appliquer les migrations
        print("\n2. Application de la migration...")
        ret = run_command([str(VENV_PYTHON), 'manage.py', 'migrate', 'tasks'])
        
        if ret == 0:
            print("\n✅ Migration appliquée avec succès!")
        else:
            print("\n❌ Erreur lors de l'application de la migration")
    else:
        print("\n❌ Erreur lors de la création de la migration")
    
    print("\n" + "=" * 60)
    input("Appuyez sur Entrée pour quitter...")
