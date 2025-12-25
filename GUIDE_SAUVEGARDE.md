# 📦 Guide de Sauvegarde et Restauration

## ✅ Configuration Actuelle

- **Destination OneDrive** : `C:\Users\Social Media Manager\OneDrive\Torii-management`
- **Format** : Fichiers `.zip` horodatés (ex: `school_backup_20251225_101541.zip`)
- **Contenu** : Base de données PostgreSQL complète + Dossier media

## 🔄 Sauvegarde Automatique

### Créer une sauvegarde complète

```powershell
.\backup_data.ps1
```

**Ce qui est sauvegardé** :
- ✅ Toute la base de données (students, prospects, finance, academics, inventory, etc.)
- ✅ Tous les nouveaux champs (ramadan, frais, modality, etc.)
- ✅ Tous les fichiers media (photos, documents)

### Options avancées

```powershell
# Sauvegarder seulement la base de données
.\backup_data.ps1 -OnlyDb

# Sauvegarder seulement les fichiers media
.\backup_data.ps1 -OnlyMedia

# Sauvegarder vers un autre dossier
.\backup_data.ps1 -Dest "D:\Backups"
```

## 🔙 Restauration

### Restaurer la dernière sauvegarde automatiquement

```powershell
.\restore_data_latest.ps1
```

**⚠️ ATTENTION** : Cela écrasera TOUTES les données actuelles !

### Restaurer une sauvegarde spécifique

```powershell
.\restore_data_latest.ps1 -File "C:\Users\Social Media Manager\OneDrive\Torii-management\school_backup_20251225_101541.zip"
```

### Options de restauration

```powershell
# Restaurer seulement la base de données
.\restore_data_latest.ps1 -OnlyDb

# Restaurer seulement les fichiers media
.\restore_data_latest.ps1 -OnlyMedia
```

## 📅 Tâche Planifiée (Recommandé)

Pour automatiser les sauvegardes quotidiennes :

1. Ouvrir **Planificateur de tâches Windows**
2. Créer une tâche qui exécute :
   ```
   powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Social Media Manager\Documents\codes\school_management\backup_data.ps1"
   ```
3. Programmer l'exécution chaque jour à minuit

## 🔍 Vérifier les sauvegardes

```powershell
# Lister toutes les sauvegardes
Get-ChildItem "C:\Users\Social Media Manager\OneDrive\Torii-management" -Filter "school_backup_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object Name,LastWriteTime,@{N='SizeMB';E={[math]::Round($_.Length/1MB,2)}}
```

## ✅ Données Sauvegardées

**Tables principales** :
- ✅ Students (étudiants avec tous les champs)
- ✅ Prospects (avec conversion tracking)
- ✅ Enrollments (inscriptions)
- ✅ Cohorts (groupes avec modality, is_individual)
- ✅ Subjects (langues)
- ✅ Payments (paiements)
- ✅ StudentAnnualFee (frais annuels avec ramadan)
- ✅ TeacherPayroll (paie professeurs)
- ✅ CashTransaction (caisse)
- ✅ InventoryItem (inventaire)
- ✅ AcademicYear (années académiques)
- ✅ Documents
- ✅ Tous les fichiers media

**Aucune perte de données** - Tout est inclus ! 🎯
