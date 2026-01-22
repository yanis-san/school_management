# 🎯 SUPABASE INTEGRATION - QUICK START

## ⚡ Démarrage rapide (3 étapes)

### 1️⃣ Configuration Supabase
```bash
python setup_supabase.py
```

Cela va vous demander vos identifiants Supabase et créer automatiquement le fichier `.env`.

**Où trouver vos identifiants :**
- 🔗 Allez à https://app.supabase.com
- 📁 Sélectionnez votre projet
- ⚙️ Settings → Database → Connection Info

### 2️⃣ Tester la connexion
```bash
python test_supabase_connection.py
```

Cela va vérifier que tout fonctionne correctement.

### 3️⃣ Démarrer l'application
```bash
python manage.py runserver
```

---

## 🔄 Basculer entre Local et Supabase

### ✅ Utiliser SUPABASE
Éditez `.env` :
```env
USE_SUPABASE=true
SUPABASE_DB_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
SUPABASE_URL=https://your_project.supabase.co
SUPABASE_KEY=your_anon_key
```

### ✅ Utiliser BASE DE DONNÉES LOCALE
Éditez `.env` :
```env
USE_SUPABASE=false
```

Changement pris en compte au prochain redémarrage !

---

## 📊 Vérifier votre configuration

```bash
# Ouvrir Django Shell
python manage.py shell
```

```python
from django.db import connection
from supabase_utils import SupabaseManager

# Afficher les infos
db_info = SupabaseManager.get_db_info()
for key, value in db_info.items():
    print(f"{key}: {value}")
```

---

## 💻 Utiliser Supabase Client dans votre code

```python
from supabase_utils import SupabaseManager

# Récupérer tous les cohorts
cohorts = SupabaseManager.select_all('academics_cohort')

# Récupérer un cohort
cohort = SupabaseManager.select_one('academics_cohort', 'id', 1)

# Créer
new_cohort = SupabaseManager.insert('academics_cohort', {
    'name': 'Nouveau Cohort',
    'start_date': '2026-01-01',
})

# Mettre à jour
SupabaseManager.update('academics_cohort', 'id', 1, {'name': 'Nom Modifié'})

# Supprimer
SupabaseManager.delete('academics_cohort', 'id', 1)
```

---

## 🐛 Troubleshooting

### "could not connect to server"
- ✅ Vérifiez votre password
- ✅ Vérifiez que le host Supabase est correct
- ✅ Vérifiez que `sslmode=require` est activé

### "role 'postgres' does not exist"
- ✅ Le dump SQL a été corrigé automatiquement

### Créer un fichier `.env` personnalisé
Copiez `.env.example` et modifiez les valeurs :
```bash
cp .env.example .env
# Éditez .env avec vos identifiants
```

---

## 📚 Documentation complète
Voir [GUIDE_SUPABASE_DJANGO.md](./GUIDE_SUPABASE_DJANGO.md) pour plus de détails.

---

## ✨ Vous êtes prêt !

```bash
# Un dernier test ?
python test_supabase_connection.py

# Puis démarrez !
python manage.py runserver
```

Votre application est maintenant configurée avec Supabase ! 🎉
