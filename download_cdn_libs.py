#!/usr/bin/env python
"""
Script pour télécharger les CDNs et les placer dans le dossier static
"""
import os
import requests
from pathlib import Path

# Créer les répertoires s'ils n'existent pas
STATIC_DIR = Path("static")
JS_DIR = STATIC_DIR / "js"
CSS_DIR = STATIC_DIR / "css"

JS_DIR.mkdir(parents=True, exist_ok=True)
CSS_DIR.mkdir(parents=True, exist_ok=True)

# Définir les fichiers à télécharger
DOWNLOADS = {
    # Tailwind CSS
    "https://cdn.tailwindcss.com": JS_DIR / "tailwind.min.js",
    
    # HTMX
    "https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js": JS_DIR / "htmx.min.js",
    
    # Alpine.js
    "https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js": JS_DIR / "alpinejs.min.js",
    
    # Chart.js
    "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js": JS_DIR / "chart.umd.js",
}

print("📥 Téléchargement des libraires CDN...")
print("-" * 50)

for url, filepath in DOWNLOADS.items():
    try:
        print(f"⏳ Téléchargement: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        size_kb = filepath.stat().st_size / 1024
        print(f"✅ Sauvegardé: {filepath.name} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"❌ Erreur: {filepath.name} - {str(e)}")

print("-" * 50)
print("✨ Terminé! Les libraires sont dans static/js/")
