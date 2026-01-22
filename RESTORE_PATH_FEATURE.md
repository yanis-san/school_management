# 🆕 Nouvelle Fonctionnalité: Restauration depuis Chemin Personnalisé

## 📋 Résumé

La commande `db_backup` supporte maintenant **3 modes de restauration**:

1. **Dernier backup** (OneDrive) - `--restore`
2. **Fichier spécifique** (OneDrive) - `--restore-file`
3. **Chemin personnalisé** ⭐ **NOUVEAU** - `--restore-path`

---

## 🎯 Cas d'Usage

### Scénario 1: Vous êtes sur un AUTRE PC
```bash
# Vous avez téléchargé un backup depuis OneDrive
python manage.py db_backup --restore-path "C:\Users\YourName\Downloads\backup.sql.gz"
```

### Scénario 2: Backup stocké localement
```bash
# Fichier dans le même dossier que le projet
python manage.py db_backup --restore-path "./backup.sql.gz"

# Fichier dans un dossier spécifique
python manage.py db_backup --restore-path "D:\Backups\db_backup_2026.sql.gz"
```

### Scénario 3: Déploiement multi-environnements
```bash
# Sur chaque machine, vous téléchargez le backup puis restaurez
python manage.py db_backup --restore-path "/path/to/downloaded/backup.sql.gz"
```

---

## 🔧 Détails Techniques

### Syntaxe Complète

```bash
python manage.py db_backup --restore-path <CHEMIN>
```

### Types de Chemins Supportés

| Type | Exemple | Notes |
|------|---------|-------|
| Absolu Windows | `C:\Backups\backup.sql.gz` | Chemin complet avec lettre de disque |
| Relatif | `./backup.sql.gz` | Relatif au dossier actuel |
| Dossier parent | `../backup.sql.gz` | Navigation dans les dossiers |
| OneDrive | `D:\OneDrive\...\backup.sql.gz` | Synchronisé localement |
| Réseau UNC | `\\serveur\partage\backup.sql.gz` | Partage réseau |

### Processus de Restauration

```
1. Utilisateur fournit un chemin
                ↓
2. Système vérifie que le fichier existe
                ↓
3. Système résout le chemin absolu
                ↓
4. Système cherche le fichier .json de métadonnées
                ↓
5. Si trouvé: Vérification du hash SHA256
   Si non trouvé: Avertissement, mais continue
                ↓
6. Demande de confirmation (YES/NO)
                ↓
7. Décompression du fichier .gz
                ↓
8. Restauration via pg_restore
                ↓
9. Vérification de la connexion DB
                ↓
10. ✅ SUCCÈS ou ❌ ERREUR
```

---

## 📝 Exemples Pratiques

### Exemple 1: Restaurer un backup téléchargé
```bash
# Le fichier est dans Downloads
python manage.py db_backup --restore-path "C:\Users\Social Media Manager\Downloads\backup_institut_torii_db_20260122_143025.sql.gz"

# Résultat:
# 📂 Backup trouvé: C:\Users\Social Media Manager\Downloads\backup_institut_torii_db_20260122_143025.sql.gz
# ✅ Intégrité vérifiée (hash: a1b2c3d4e5f6...)
# ⚠️ ATTENTION: Cette action va REMPLACER la base de données actuelle. Êtes-vous sûr? (yes/no): yes
# 📥 Restauration en cours...
# ✅ Restauration réussie!
```

### Exemple 2: Restaurer depuis OneDrive local
```bash
python manage.py db_backup --restore-path "D:\OneDrive\Torii-management\backups\backup_institut_torii_db_20260122_143025.sql.gz"
```

### Exemple 3: Sauvegarder puis restaurer localement
```bash
# 1. Créer un backup (normal)
python manage.py db_backup

# 2. Copier le fichier depuis OneDrive vers un dossier local
# Copier: C:\Users\...\OneDrive\Torii-management\backups\backup_*.sql.gz
# Vers:   C:\Backups\

# 3. Restaurer depuis le chemin local
python manage.py db_backup --restore-path "C:\Backups\backup_institut_torii_db_20260122_143025.sql.gz"
```

---

## 🛡️ Sécurité et Vérifications

### ✅ Vérifications Automatiques

1. **Fichier existe?** - OUI → Continue | NON → ❌ Erreur
2. **Métadonnées présentes?** - OUI → Vérifier hash | NON → ⚠️ Avertissement (continue quand même)
3. **Hash valide?** - OUI → Continue | NON → ❌ Erreur (fichier corrompu)
4. **Confirmation utilisateur?** - OUI → Restaure | NON → ❌ Annulé

### ⚠️ Points Importants

- Les fichiers `.json` (métadonnées) sont **optionnels** mais **recommandés**
- Si le `.json` est absent, la vérification d'intégrité est ignorée
- **TOUJOURS** avoir une copie de sauvegarde avant de restaurer
- La restauration demande **TOUJOURS** une confirmation

---

## 📊 Comparaison des Modes

| Aspect | `--restore` | `--restore-file` | `--restore-path` |
|--------|------------|-----------------|-----------------|
| Cherche le dernier | ✅ Oui | ❌ Non | ❌ Non |
| Cherche dans OneDrive | ✅ Oui | ✅ Oui | ❌ Non |
| Chemin personnalisé | ❌ Non | ❌ Non | ✅ Oui |
| Autre machine | ❌ Non | ❌ Non | ✅ Oui |
| Idéal pour | Restauration rapide | Choix du backup | Déploiement multi-PC |

---

## 🚀 Workflow Recommandé

### Pour un Nouveau Déploiement

```bash
# 1. Sur le PC source
cd C:\Users\Social Media Manager\Documents\codes\school_management
python manage.py db_backup
# Fichier créé dans OneDrive

# 2. Sur le PC destination (après clonage du projet)
# - Télécharger le backup depuis OneDrive
# - Le placer dans un dossier: C:\Backups\

# 3. Restaurer le backup
python manage.py db_backup --restore-path "C:\Backups\backup_institut_torii_db_20260122_143025.sql.gz"

# 4. Vérifier le succès
python manage.py check
python manage.py shell
>>> from academics.models import Cohort
>>> Cohort.objects.count()
```

### Pour un Backup de Sécurité Régulier

```bash
# Script: backup_secure.bat
@echo off
cd C:\Users\Social Media Manager\Documents\codes\school_management
call .venv\Scripts\activate.bat
python manage.py db_backup
echo Backup créé à %date% %time%
pause
```

---

## 🆘 Troubleshooting

### Problème: "Fichier non trouvé"
```
❌ Fichier non trouvé: C:\Backups\backup.sql.gz
```
**Solution**: Vérifiez le chemin exact. Utilisez `dir` pour lister les fichiers.

### Problème: "Erreur d'intégrité"
```
❌ Erreur d'intégrité! Le backup a été corrompu.
```
**Solution**: Le fichier `.gz` a été endommagé. Téléchargez-le à nouveau depuis OneDrive.

### Problème: "Chemin réseau invalide"
```
❌ Fichier non trouvé: \\serveur\partage\backup.sql.gz
```
**Solution**: Vérifiez que le partage réseau est accessible. Utilisez `ping` ou `net use`.

### Problème: "Métadonnées non trouvées"
```
⚠️ Métadonnées non trouvées. Vérification du hash impossible.
```
**Explication**: Le fichier `.json` est absent (normal si c'est un ancien backup). Le système continue quand même.

---

## 📞 Questions Fréquentes

**Q: Puis-je restaurer depuis OneDrive directement?**
A: Oui! Si le dossier OneDrive est synchronisé localement:
```bash
python manage.py db_backup --restore-path "D:\OneDrive\Torii-management\backups\backup.sql.gz"
```

**Q: Le fichier .json est-il obligatoire?**
A: Non, mais recommandé. Sans .json, la vérification d'intégrité ne peut pas se faire.

**Q: Puis-je utiliser des chemins UNC?**
A: Oui! Exemple: `\\mon-nas\backups\backup.sql.gz`

**Q: Que se passe-t-il si j'annule la restauration?**
A: La base de données ne sera pas modifiée. Aucune donnée n'est perdue.

**Q: Comment savoir si la restauration a réussi?**
A: Le système affiche `✅ Restauration réussie!` et teste la connexion à la BD.

---

## ✅ Résumé

| Fonctionnalité | ✅ Implémentée |
|---|---|
| Restauration depuis chemin absolu | ✅ Oui |
| Restauration depuis chemin relatif | ✅ Oui |
| Vérification d'intégrité SHA256 | ✅ Oui |
| Support métadonnées optionnelles | ✅ Oui |
| Confirmation avant restauration | ✅ Oui |
| Compatibilité multi-PC | ✅ Oui |

**Date**: 22 Janvier 2026  
**Version**: 2.0 (avec `--restore-path`)  
**État**: ✅ Production-Ready
