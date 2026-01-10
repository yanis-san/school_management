# 📦 Guide Complet de Sauvegarde et Restauration

## 🎯 Ce qui est sauvegardé automatiquement

### 1. Base de données PostgreSQL
- Toutes les tables et données
- Toutes les migrations appliquées (y compris les nouvelles)
- Structure complète de la base

### 2. Fichiers Media (dossier `media/`)
Tous les fichiers uploadés par les utilisateurs :
- ✅ **Reçus de paiement** (`media/payment_receipts/`)
- ✅ Photos de profil des étudiants
- ✅ Documents administratifs
- ✅ Certificats et attestations
- ✅ Tous les autres fichiers uploadés

### 3. Manifeste de sauvegarde
- Date et heure de création
- Version de Django
- Chemins complets
- Type de base de données

---

## 📥 Créer une sauvegarde

### Sauvegarde complète (RECOMMANDÉ)
```powershell
.\backup_data.ps1
```
Sauvegarde la base de données ET tous les fichiers media.

### Sauvegarde de la base uniquement
```powershell
.\backup_data.ps1 -OnlyDb
```
Plus rapide, mais ne sauvegarde pas les fichiers (reçus, photos, etc.)

### Sauvegarde des fichiers uniquement
```powershell
.\backup_data.ps1 -OnlyMedia
```
Sauvegarde uniquement les fichiers media (pas la base de données)

### Sauvegarde vers un dossier spécifique
```powershell
.\backup_data.ps1 -Dest "D:\MesSauvegardes"
```

---

## 📤 Restaurer une sauvegarde

### ⚠️ ATTENTION - Restauration = Remplacement total
La restauration **écrase complètement** :
- La base de données actuelle
- Tous les fichiers media actuels

**Une copie locale de sécurité** est automatiquement créée dans `backups_local/` avant chaque restauration.

### Restaurer la dernière sauvegarde (FORCE)
```powershell
.\restore_data_latest.ps1
```
Restaure automatiquement la sauvegarde la plus récente.

### Restaurer une sauvegarde spécifique
```powershell
.\restore_data_latest.ps1 -File "C:\path\to\school_backup_20260108_110353.zip"
```

### Lister toutes les sauvegardes disponibles
```powershell
.\.venv\Scripts\python.exe manage.py restore_data --list
```

### Restaurer uniquement la base de données
```powershell
.\restore_data_latest.ps1 -OnlyDb
```
Restaure la base mais garde les fichiers actuels.

### Restaurer uniquement les fichiers media
```powershell
.\restore_data_latest.ps1 -OnlyMedia
```
Restaure les fichiers mais garde la base actuelle.

---

## 🔍 Vérifier le contenu d'une sauvegarde

### Lister le contenu d'une sauvegarde
```powershell
$backup = "C:\Users\Social Media Manager\OneDrive\Torii-management\school_backup_XXXXXXXX_XXXXXX.zip"
.\.venv\Scripts\python.exe -c "import zipfile; z = zipfile.ZipFile('$backup'); [print(f) for f in z.namelist()]"
```

### Vérifier si les reçus de paiement sont sauvegardés
```powershell
$latestBackup = Get-ChildItem "C:\Users\Social Media Manager\OneDrive\Torii-management\school_backup_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
.\.venv\Scripts\python.exe -c "import zipfile; z = zipfile.ZipFile('$($latestBackup.FullName)'); receipts = [f for f in z.namelist() if 'payment_receipts' in f]; print(f'✅ {len(receipts)} reçus trouvés'); [print(f'  - {r}') for r in receipts[:10]]"
```

---

## 🗂️ Organisation des sauvegardes

### Dossier principal (OneDrive)
```
C:\Users\Social Media Manager\OneDrive\Torii-management\
├── school_backup_20260108_110353.zip  ← Plus récente
├── school_backup_20260107_153022.zip
├── school_backup_20260106_091545.zip
└── ...
```

### Sauvegardes locales de sécurité
Créées automatiquement avant chaque restauration :
```
C:\Users\Social Media Manager\Documents\codes\school_management\backups_local\
├── db_pre_restore_20260108_110500.sqlite3
├── media_pre_restore_20260108_110500/
│   ├── payment_receipts/
│   │   └── 2026/01/benali.pdf
│   └── ...
└── ...
```

---

## ⏰ Automatisation recommandée

### Sauvegarde quotidienne automatique (à configurer)

1. Ouvrir le **Planificateur de tâches Windows**
2. Créer une nouvelle tâche :
   - **Nom** : Sauvegarde quotidienne School Management
   - **Déclencheur** : Tous les jours à 23h00
   - **Action** : 
     ```
     Programme : powershell.exe
     Arguments : -File "C:\Users\Social Media Manager\Documents\codes\school_management\backup_data.ps1"
     Répertoire : C:\Users\Social Media Manager\Documents\codes\school_management
     ```

---

## 📊 Nouvelles migrations incluses

Les sauvegardes incluent automatiquement toutes les migrations, notamment :

### Finance
- `0007_payment_receipt.py` - Ajout du champ reçu/justificatif pour les paiements
- Toutes les autres migrations existantes

### Lors de la restauration
Après une restauration, **aucune migration supplémentaire** n'est nécessaire car :
1. La base de données restaurée contient déjà la structure à jour
2. Les fichiers de migration sont dans le code source (pas dans la sauvegarde)

⚠️ **Important** : Si vous restaurez sur une nouvelle machine, assurez-vous que :
- Le code source est à jour avec toutes les migrations
- L'environnement virtuel est installé avec toutes les dépendances

---

## 🆘 En cas de problème

### La sauvegarde échoue
```powershell
# Vérifier que PostgreSQL est accessible
pg_dump --version

# Vérifier l'environnement virtuel
.\.venv\Scripts\python.exe --version

# Vérifier les permissions du dossier OneDrive
Test-Path "C:\Users\Social Media Manager\OneDrive\Torii-management" -PathType Container
```

### La restauration échoue
```powershell
# Vérifier que psql est installé
psql --version

# Restaurer manuellement la base
psql -h localhost -U postgres -d school_db < db_postgres_20260108_110353.sql

# Restaurer manuellement les fichiers media depuis backups_local/
```

### Les fichiers payment_receipts ne sont pas sauvegardés
Vérifier que le dossier existe :
```powershell
Test-Path "media\payment_receipts"
```

Si non, le créer :
```powershell
New-Item -ItemType Directory -Force -Path "media\payment_receipts"
```

---

## ✅ Checklist avant restauration importante

- [ ] Vérifier la date de la sauvegarde à restaurer
- [ ] S'assurer que le serveur Django est arrêté
- [ ] Vérifier l'espace disque disponible (au moins 2x la taille de la sauvegarde)
- [ ] Avoir un backup local récent (automatique mais vérifier)
- [ ] Avertir les utilisateurs que le système sera indisponible

---

## 🎓 Exemples de scénarios

### Scénario 1 : Migration vers nouveau serveur
```powershell
# Sur l'ancien serveur
.\backup_data.ps1

# Copier le fichier .zip vers le nouveau serveur
# Sur le nouveau serveur (après installation)
.\restore_data_latest.ps1 -File "school_backup_20260108_110353.zip"
```

---

## 🖥️ Restauration sur un nouveau PC (procédure complète)

1) **Cloner le projet**
```powershell
cd C:\Users\<vous>\Documents\codes
git clone https://github.com/<votre_repo>/school_management.git
cd school_management
```

2) **Créer l'environnement virtuel + dépendances**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

3) **Placer la sauvegarde (.zip)**
- Copier le fichier `school_backup_YYYYMMDD_HHMMSS.zip` dans un dossier accessible (ex: `C:\Backups\`)
- Si OneDrive n'est pas au même chemin, passez le chemin explicitement avec `-File`

4) **Configurer la base PostgreSQL (si nécessaire)**
- Créer une base vide avec les mêmes credentials que `config/settings.py` (NAME/USER/PASSWORD/HOST/PORT)
- Installer les outils client PostgreSQL (`psql`, `pg_restore`), ou préciser `--psql` si hors PATH

5) **Restaurer (DB + media)**
```powershell
.\restore_data_latest.ps1 -File "C:\Backups\school_backup_20260108_110353.zip" -Force
```
- Utilisez `-OnlyDb` ou `-OnlyMedia` si besoin d'une restauration partielle

6) **Vérifier**
- Lancer le serveur :
```powershell
.\.venv\Scripts\python.exe manage.py runserver
```
- Vérifier que les reçus sont présents : `media/payment_receipts/...`
- Vérifier quelques élèves et paiements dans l'interface

> **Note** : Pas besoin de rejouer les migrations après restauration de la DB, elle contient déjà le schéma à jour.


### Scénario 2 : Erreur de saisie massive
```powershell
# Restaurer la sauvegarde d'avant l'erreur
.\restore_data_latest.ps1 -File "school_backup_20260108_090000.zip"
```

### Scénario 3 : Test de nouvelles fonctionnalités
```powershell
# Backup avant tests
.\backup_data.ps1 -Dest "D:\BackupTests"

# ... faire les tests ...

# Si problème : restaurer
.\restore_data_latest.ps1 -File "D:\BackupTests\school_backup_*.zip"
```

---

## 📞 Support

En cas de problème avec les sauvegardes, consulter :
1. Les logs dans le terminal après exécution
2. Le fichier `manifest.json` dans la sauvegarde ZIP
3. Les copies de sécurité dans `backups_local/`

**Date de dernière mise à jour** : 8 janvier 2026
**Version du système** : Django avec PostgreSQL
