# 💾 Système de Sauvegarde et Restauration - Guide Complet

## 🎯 Objectif

Créer un système **SIMPLE, SÉCURISÉ et FIABLE** pour:
- ✅ Sauvegarder la base de données PostgreSQL
- ✅ Restaurer facilement n'importe quel backup
- ✅ Vérifier l'intégrité des données
- ✅ Protéger contre la perte de données

---

## 🚀 Démarrage Rapide

### Option 1: Via Terminal (Recommandé pour l'automatisation)

```bash
# Créer une sauvegarde
python manage.py db_backup

# Restaurer le dernier backup (OneDrive)
python manage.py db_backup --restore

# Restaurer un backup spécifique (OneDrive)
python manage.py db_backup --restore-file backup_institut_torii_db_20260122_143025.sql.gz

# Restaurer depuis un chemin absolu ou relatif ⭐ NOUVEAU
python manage.py db_backup --restore-path "C:\Backups\backup_institut_torii_db_20260122_143025.sql.gz"
python manage.py db_backup --restore-path "./backup.sql.gz"
python manage.py db_backup --restore-path "D:\OneDrive\Torii-management\backups\backup.sql.gz"

# Lister tous les backups
python manage.py db_backup --list

# Vérifier l'intégrité du dernier backup
python manage.py db_backup --verify

# Afficher les statistiques
python manage.py db_backup --info
```

### Option 2: Via Interface Web (Interface Admin)

1. Allez à: `http://localhost:8000/admin/`
2. Cherchez le lien **💾 Gestion des Sauvegardes**
3. Cliquez sur **🔄 Créer une Sauvegarde**
4. Pour restaurer, cliquez sur **📥 Restaurer** à côté du backup

---

## 📊 Où sont stockées les sauvegardes?

```
C:\Users\Social Media Manager\OneDrive\Torii-management\backups\
```

Chaque backup contient:
- `backup_institut_torii_db_YYYYMMDD_HHMMSS.sql.gz` - Fichier compressé
- `backup_institut_torii_db_YYYYMMDD_HHMMSS.json` - Métadonnées et hash

---

## 🔒 Sécurité et Vérifications

### 1. **Hash SHA256** - Vérification d'intégrité
Chaque backup a un hash SHA256 qui garantit que le fichier n'a pas été corrompu.

```bash
# Vérifier automatiquement
python manage.py db_backup --verify
```

### 2. **Métadonnées JSON** - Infos du backup
```json
{
  "backup_file": "backup_institut_torii_db_20260122_143025.sql.gz",
  "timestamp": "20260122_143025",
  "datetime": "2026-01-22T14:30:25.123456",
  "database": "institut_torii_db",
  "size_bytes": 52428800,
  "hash": "a1b2c3d4e5f6...",
  "status": "completed"
}
```

### 3. **Compression GZIP**
Les fichiers sont compressés pour économiser l'espace (typiquement -70% de taille).

### 4. **Confirmation avant restauration**
Avant de restaurer, le système demande une confirmation:
```
⚠️ ATTENTION: Cette action va REMPLACER la base de données actuelle. Êtes-vous sûr? (yes/no):
```

---

## 📝 Flux de Sauvegarde

```
┌─────────────────────────────────┐
│ 1. Créer Backup                │
│    python manage.py db_backup  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 2. Dump de la BD (pg_dump)      │
│    Format: Custom (binaire)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 3. Compression GZIP             │
│    Réduit la taille             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 4. Calcul du Hash SHA256        │
│    Vérification d'intégrité     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 5. Création Métadonnées JSON    │
│    Infos + Hash                 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 6. Sauvegarde sur OneDrive      │
│    Dossier: Torii-management    │
└─────────────────────────────────┘
```

---

## 📥 Flux de Restauration

```
┌────────────────────────────────────┐
│ 1. Sélectionner Backup             │
│    Choisir le fichier à restaurer  │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 2. Vérifier Hash                   │
│    Comparer fichier vs métadonnées │
└───────────┬────────────────────────┘
            │
     ┌──────┴──────┐
     │             │
     ▼             ▼
    ✅OK        ❌Corrompu
     │             │
     │             ▼
     │    ❌ ARRÊT - Erreur d'intégrité
     │
     ▼
┌────────────────────────────────────┐
│ 3. Demander Confirmation           │
│    ⚠️ Confirmation requise         │
└───────────┬────────────────────────┘
            │
     ┌──────┴──────┐
     │             │
     ▼             ▼
   YES           NO
     │             │
     │             ▼
     │    ❌ Annulé
     │
     ▼
┌────────────────────────────────────┐
│ 4. Décompresser                    │
│    GZIP → SQL                      │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 5. Restaurer (pg_restore)          │
│    --clean --if-exists             │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 6. Vérifier Intégrité              │
│    Tester connexion à la BD        │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ ✅ RESTAURATION RÉUSSIE            │
└────────────────────────────────────┘
```

---

## 🔄 Cas d'Usage Courants

### Scénario 1: Backup quotidien automatisé

```bash
# Créer un script batch (Windows)
# File: backup_auto.bat

@echo off
cd C:\Users\Social Media Manager\Documents\codes\school_management
call .venv\Scripts\activate.bat
python manage.py db_backup
echo Backup terminé à %date% %time%
```

Puis ajouter une tâche programmée Windows:
- Fréquence: Tous les jours à 23:00
- Commande: `C:\chemin\backup_auto.bat`

### Scénario 2: Avant une migration majeure

```bash
# 1. Créer un backup de sécurité
python manage.py db_backup

# 2. Faire la migration
python manage.py migrate

# 3. Si problème, restaurer
python manage.py db_backup --restore
```

### Scénario 3: Cloner la BD sur une nouvelle machine

```bash
# Sur la machine source
python manage.py db_backup

# Copier le fichier backup sur OneDrive

# Sur la machine de destination
python manage.py db_backup --restore-file backup_institut_torii_db_20260122_143025.sql.gz
```

### Scénario 4: Restaurer un backup d'un autre ordinateur ⭐ NOUVEAU

**Situation**: Vous avez téléchargé un backup depuis OneDrive sur une autre machine et vous voulez le restaurer.

```bash
# Depuis un chemin absolu (Windows)
python manage.py db_backup --restore-path "C:\Users\YourName\Downloads\backup_institut_torii_db_20260122_143025.sql.gz"

# Depuis un chemin relatif (même dossier que le projet)
python manage.py db_backup --restore-path "./backup.sql.gz"

# Depuis un chemin réseau (OneDrive)
python manage.py db_backup --restore-path "D:\OneDrive\Torii-management\backups\backup_institut_torii_db_20260122_143025.sql.gz"

# Le système va automatiquement:
# 1. Trouver le fichier au chemin spécifié
# 2. Chercher le fichier .json de métadonnées
# 3. Vérifier l'intégrité du backup
# 4. Demander une confirmation
# 5. Restaurer la base de données
```

---

## 📥 Les 3 Modes de Restauration

### 1️⃣ Mode 1: Dernier Backup (OneDrive)
```bash
python manage.py db_backup --restore
```
- Restaure le **dernier** backup du dossier OneDrive
- Idéal pour une restauration rapide après un problème
- Exemple: `backup_institut_torii_db_20260122_143025.sql.gz`

### 2️⃣ Mode 2: Fichier Spécifique (OneDrive)
```bash
python manage.py db_backup --restore-file backup_institut_torii_db_20260122_143025.sql.gz
```
- Restaure un fichier **spécifique** du dossier OneDrive
- Idéal pour choisir entre plusieurs backups
- Utiliser `--list` pour voir les fichiers disponibles

### 3️⃣ Mode 3: Chemin Personnalisé ⭐ NOUVEAU
```bash
# Chemin absolu
python manage.py db_backup --restore-path "C:\Backups\backup.sql.gz"

# Chemin relatif
python manage.py db_backup --restore-path "./backup.sql.gz"

# Chemin UNC (réseau)
python manage.py db_backup --restore-path "\\serveur\partage\backup.sql.gz"
```
- Restaure depuis **n'importe quel chemin** sur votre ordinateur
- Idéal pour les sauvegardes téléchargées depuis OneDrive
- Idéal pour les déploiements sur d'autres machines
- Support complet des chemins Windows

---

## ⚠️ Points Importants

### ✅ À FAIRE:

1. **Vérifier régulièrement** que les backups se créent
   ```bash
   python manage.py db_backup --list
   ```

2. **Tester la restauration** régulièrement (au moins 1x par mois)

3. **Garder plusieurs backups** (au moins 7-10 derniers)

4. **Vérifier l'espace disque** sur OneDrive

5. **Documenter les données sensibles** sauvegardées

### ❌ À ÉVITER:

1. **Ne pas supprimer les métadonnées .json** (nécessaire pour la vérification)

2. **Ne pas restaurer sans confirmation**

3. **Ne pas arrêter la restauration en cours** (peut corrompre la BD)

4. **Ne pas modifier les fichiers de backup** (invalide le hash)

5. **Ne pas oublier le backup avant les modifications majeures**

---

## 🆘 Troubleshooting

### Problème: "pg_dump: command not found"

**Solution:** PostgreSQL n'est pas dans le PATH. Ajouter:
```
C:\Program Files\PostgreSQL\16\bin
```
au PATH Windows.

### Problème: "Erreur d'intégrité! Fichier corrompu!"

**Solution:** Le fichier backup a été endommagé. Options:
1. Utiliser un backup plus ancien
2. Vérifier l'espace disque OneDrive
3. Recréer un backup

### Problème: "Restauration échouée"

**Solutions possibles:**
1. Vérifier que PostgreSQL fonctionne
2. Vérifier les identifiants dans `settings.py`
3. S'assurer que la base de données existe
4. Consulter les logs PostgreSQL

### Problème: "Fichier très volumineux"

**Solutions:**
1. Utiliser une compression locale d'abord
2. Nettoyer la BD (supprimer les vieilles données)
3. Archiver les backups anciens

---

## 📊 Bonnes Pratiques

### Calendrier de Sauvegarde Recommandé

| Fréquence | Timing | Rétention |
|-----------|--------|-----------|
| Quotidien | 23:00 | 7 jours |
| Hebdo | Dimanche 02:00 | 4 semaines |
| Mensuel | 1er du mois 03:00 | 12 mois |

### Vérification d'Intégrité

```bash
# Hebdomadaire
python manage.py db_backup --verify

# Avant importants changements
python manage.py db_backup --verify
```

---

## 📞 Support

Pour plus d'aide, consultez:
- [Documentation PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
- [Documentation Django Management Commands](https://docs.djangoproject.com/en/6.0/howto/custom-management-commands/)
- Logs dans: `C:\Users\Social Media Manager\OneDrive\Torii-management\backups\`

---

## ✅ Résumé

| Aspect | ✅ Couvert |
|--------|-----------|
| Sauvegarde simple | ✅ `python manage.py db_backup` |
| Interface web | ✅ Admin Django /admin/backup/ |
| Vérification intégrité | ✅ Hash SHA256 automatique |
| Sécurité restauration | ✅ Confirmation + vérification |
| Stockage OneDrive | ✅ Synchronisé automatiquement |
| Métadonnées | ✅ JSON pour chaque backup |
| Récupération | ✅ Plusieurs backups conservés |

**État**: ✅ Production-Ready  
**Date**: 22 Janvier 2026
