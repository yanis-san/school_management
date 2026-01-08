#!/usr/bin/env python
"""
Script pour démarrer l'application Django et ouvrir le navigateur automatiquement.
À exécuter depuis la racine du projet.
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

# Déterminer le chemin du projet
PROJECT_DIR = Path(__file__).resolve().parent

# Chemin vers le venv
VENV_PYTHON = PROJECT_DIR / '.venv' / 'Scripts' / 'python.exe'

# URL du serveur (IP statique fixée pour hotspot)
SERVER_URL = 'http://192.168.43.200:8000'

def check_venv():
    """Vérifier que le venv existe"""
    if not VENV_PYTHON.exists():
        print(f"❌ Erreur: Le venv n'a pas été trouvé à {VENV_PYTHON}")
        print("Assurez-vous que le virtual environment est configuré.")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)

def check_port():
    """Vérifier si le port 8000 est disponible"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    return result != 0  # True si port libre

def start_server():
    """Démarrer le serveur Django"""
    print("🚀 Démarrage du serveur Django...")
    os.chdir(PROJECT_DIR)
    
    # Démarrer le serveur dans un nouveau processus
    cmd = [
        str(VENV_PYTHON),
        'manage.py',
        'runserver',
        '0.0.0.0:8000'
    ]
    
    # Créer un nouveau processus sans bloquer
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE  # Nouvelle fenêtre sur Windows
    )
    
    return process

def open_browser():
    """Affiche l'URL au lieu d'ouvrir le navigateur automatiquement"""
    print(f"⏳ Attente du démarrage du serveur...")
    time.sleep(3)
    print(f"🌐 Serveur prêt sur {SERVER_URL}")

def main():
    print("=" * 50)
    print("📚 Gestionnaire d'École - Démarrage")
    print("=" * 50)
    
    # Vérifier le venv
    check_venv()
    
    # Vérifier le port
    if not check_port():
        print("⚠️  Le port 8000 est déjà utilisé.")
        print(f"Si le serveur tourne déjà, accédez à {SERVER_URL}")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    try:
        # Démarrer le serveur
        process = start_server()
        print("✅ Serveur lancé!")
        
        # Afficher l'URL (pas d'ouverture auto)
        open_browser()
        
        print("\n" + "=" * 50)
        print("✨ L'application est prête!")
        print(f"📍 URL: {SERVER_URL}")
        print("🛑 Pour arrêter: Fermer la fenêtre du serveur")
        print("=" * 50)
        print("\n")
        
        # Attendre que l'utilisateur ferme l'application
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur...")
        process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)

if __name__ == '__main__':
    main()
