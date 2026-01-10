#!/usr/bin/env python
"""
Script pour vérifier le contenu d'une sauvegarde et afficher des statistiques détaillées.
Usage: python verify_backup.py [chemin_vers_backup.zip]
"""
import sys
import json
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime


def format_size(bytes_size):
    """Convertir les bytes en format lisible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def verify_backup(backup_path):
    """Vérifier et afficher le contenu d'une sauvegarde"""
    
    if not Path(backup_path).exists():
        print(f"❌ Fichier introuvable: {backup_path}")
        return False
    
    print("\n" + "="*70)
    print("📦 VÉRIFICATION DE SAUVEGARDE")
    print("="*70)
    print(f"\n📁 Fichier: {Path(backup_path).name}")
    print(f"📊 Taille: {format_size(Path(backup_path).stat().st_size)}")
    print(f"📅 Modifié: {datetime.fromtimestamp(Path(backup_path).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    with ZipFile(backup_path, 'r') as zf:
        # Lire le manifeste
        print("\n" + "-"*70)
        print("📋 INFORMATIONS DU MANIFESTE")
        print("-"*70)
        
        try:
            manifest_data = zf.read('manifest.json').decode('utf-8')
            manifest = json.loads(manifest_data)
            
            print(f"Projet: {manifest.get('project', 'N/A')}")
            print(f"Créé le: {manifest.get('created_at', 'N/A')}")
            print(f"Django version: {manifest.get('django_version', 'N/A')}")
            print(f"Base de données: {manifest.get('db_engine', 'N/A')}")
        except KeyError:
            print("⚠️ Manifeste introuvable")
        
        # Analyser le contenu
        all_files = zf.namelist()
        
        # Base de données
        print("\n" + "-"*70)
        print("💾 BASE DE DONNÉES")
        print("-"*70)
        
        db_files = [f for f in all_files if f.endswith('.sqlite3') or f.endswith('.sql')]
        if db_files:
            for db_file in db_files:
                info = zf.getinfo(db_file)
                print(f"✅ {db_file}")
                print(f"   Taille: {format_size(info.file_size)}")
                print(f"   Compressé: {format_size(info.compress_size)}")
        else:
            print("❌ Aucun fichier de base de données trouvé")
        
        # Fichiers media
        print("\n" + "-"*70)
        print("📁 FICHIERS MEDIA")
        print("-"*70)
        
        media_files = [f for f in all_files if f.startswith('media/') and not f.endswith('/')]
        
        if media_files:
            # Statistiques par catégorie
            categories = {}
            total_size = 0
            
            for media_file in media_files:
                info = zf.getinfo(media_file)
                total_size += info.file_size
                
                # Déterminer la catégorie
                parts = media_file.split('/')
                if len(parts) >= 2:
                    category = parts[1]  # media/payment_receipts/... -> payment_receipts
                    if category not in categories:
                        categories[category] = {'count': 0, 'size': 0, 'files': []}
                    categories[category]['count'] += 1
                    categories[category]['size'] += info.file_size
                    categories[category]['files'].append(media_file)
            
            print(f"Total fichiers: {len(media_files)}")
            print(f"Taille totale: {format_size(total_size)}")
            print()
            
            for category, data in categories.items():
                print(f"\n📂 {category}/")
                print(f"   Fichiers: {data['count']}")
                print(f"   Taille: {format_size(data['size'])}")
                
                # Afficher les 5 premiers fichiers
                if data['files']:
                    print(f"   Exemples:")
                    for f in data['files'][:5]:
                        print(f"      • {f}")
                    if len(data['files']) > 5:
                        print(f"      ... et {len(data['files']) - 5} autres")
        else:
            print("⚠️ Aucun fichier media trouvé")
        
        # Vérification spécifique des reçus de paiement
        print("\n" + "-"*70)
        print("🧾 REÇUS DE PAIEMENT")
        print("-"*70)
        
        receipts = [f for f in all_files if 'payment_receipts' in f and not f.endswith('/')]
        if receipts:
            print(f"✅ {len(receipts)} reçu(s) de paiement trouvé(s)")
            
            # Grouper par année/mois
            by_period = {}
            for receipt in receipts:
                parts = receipt.split('/')
                if len(parts) >= 4:  # media/payment_receipts/2026/01/file.pdf
                    period = f"{parts[2]}/{parts[3]}"
                    if period not in by_period:
                        by_period[period] = []
                    by_period[period].append(parts[-1])
            
            for period, files in sorted(by_period.items()):
                print(f"\n   📅 {period}:")
                for filename in files[:10]:
                    print(f"      • {filename}")
                if len(files) > 10:
                    print(f"      ... et {len(files) - 10} autres")
        else:
            print("⚠️ Aucun reçu de paiement trouvé")
        
        # Résumé final
        print("\n" + "="*70)
        print("✅ RÉSUMÉ")
        print("="*70)
        
        has_db = len(db_files) > 0
        has_media = len(media_files) > 0
        has_receipts = len(receipts) > 0
        
        print(f"Base de données: {'✅ OK' if has_db else '❌ MANQUANT'}")
        print(f"Fichiers media: {'✅ OK' if has_media else '⚠️ AUCUN'}")
        print(f"Reçus de paiement: {'✅ OK' if has_receipts else '⚠️ AUCUN'}")
        
        if has_db and (has_media or not media_files):
            print("\n✅ Cette sauvegarde est complète et peut être restaurée.")
        else:
            print("\n⚠️ Cette sauvegarde est incomplète.")
        
        print("="*70 + "\n")
    
    return True


def main():
    """Point d'entrée principal"""
    
    if len(sys.argv) > 1:
        backup_path = sys.argv[1]
    else:
        # Trouver la dernière sauvegarde
        backup_dir = Path(r"C:\Users\Social Media Manager\OneDrive\Torii-management")
        
        if not backup_dir.exists():
            print("❌ Dossier de sauvegarde introuvable")
            print(f"   Chemin: {backup_dir}")
            print("\nUsage: python verify_backup.py [chemin_vers_backup.zip]")
            return
        
        backups = sorted(backup_dir.glob("school_backup_*.zip"), 
                        key=lambda p: p.stat().st_mtime, 
                        reverse=True)
        
        if not backups:
            print(f"❌ Aucune sauvegarde trouvée dans {backup_dir}")
            print("\nUsage: python verify_backup.py [chemin_vers_backup.zip]")
            return
        
        backup_path = backups[0]
        print(f"\n🔍 Vérification de la dernière sauvegarde...")
    
    verify_backup(backup_path)


if __name__ == '__main__':
    main()
