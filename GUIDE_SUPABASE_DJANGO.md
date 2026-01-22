# 🚀 Guide Complet : Configurer Supabase avec Django

## 📋 Table des matières
1. [Prérequis](#prérequis)
2. [Configuration Supabase](#configuration-supabase)
3. [Configuration Django](#configuration-django)
4. [Basculer entre Local et Supabase](#basculer-entre-local-et-supabase)
5. [Utiliser Supabase Client](#utiliser-supabase-client)
6. [Troubleshooting](#troubleshooting)

---

## 📌 Prérequis

✅ **Déjà fait :**
- Supabase CLI installé (optionnel mais recommandé)
- `supabase-py` ajouté à requirements.txt
- Dump SQL restauré sur Supabase

✅ **À faire :**
- Créer un compte Supabase
- Créer un projet Supabase
- Récupérer vos identifiants

---

## 🔧 Configuration Supabase

### Étape 1 : Récupérer vos identifiants

1. Connectez-vous à [Supabase Dashboard](https://supabase.com/dashboard)
2. Sélectionnez votre projet
3. Allez à **Settings** → **Database**

**Vous trouverez :**
- 🔗 Connection String (PostgreSQL)
- 👤 Username (postgres)
- 🔐 Password
- 🌐 Host (xxxxx.supabase.co)
- 🔑 Anon Key et Service Role Key

### Étape 2 : Identifier votre URL PostgreSQL

La connection string ressemble à :
```
postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```

---

## ⚙️ Configuration Django

### Option 1 : Via fichier `.env` (RECOMMANDÉ)

1. Créez un fichier `.env` à la racine du projet :

```bash
# Utiliser Supabase
USE_SUPABASE=true

# Connection via URL complète (plus simple)
SUPABASE_DB_URL=postgresql://postgres:your_password@xxx.supabase.co:5432/postgres

# OU via variables individuelles
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_password
SUPABASE_DB_HOST=xxx.supabase.co
SUPABASE_DB_PORT=5432

# API Keys pour Supabase Client
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
```

2. Assurez-vous que `django-environ` est configuré dans settings.py :

```python
from dotenv import load_dotenv
load_dotenv()
```

### Option 2 : Via variables d'environnement système

**PowerShell :**
```powershell
$env:USE_SUPABASE="true"
$env:SUPABASE_DB_URL="postgresql://postgres:password@xxx.supabase.co:5432/postgres"
$env:SUPABASE_URL="https://xxx.supabase.co"
$env:SUPABASE_KEY="your_anon_key"
```

**Bash :**
```bash
export USE_SUPABASE=true
export SUPABASE_DB_URL="postgresql://postgres:password@xxx.supabase.co:5432/postgres"
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="your_anon_key"
```

---

## 🔄 Basculer entre Local et Supabase

### ✅ Utiliser BASE DE DONNÉES LOCALE
```python
# settings.py - Laissez USE_SUPABASE à false
USE_SUPABASE = False
```

```bash
# Ou dans .env
USE_SUPABASE=false
```

### ✅ Utiliser SUPABASE
```bash
# Dans .env
USE_SUPABASE=true
```

**Vérifier la configuration :**
```bash
python manage.py shell
```

```python
from django.conf import settings
from django.db import connection

# Vérifier la base de données
print(connection.settings_dict)
```

---

## 📦 Utiliser Supabase Client (Non-ORM)

### Exemple 1 : Récupérer des données via Supabase Client

```python
# views.py ou models.py
import os
from supabase import create_client, Client

# Initialiser le client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Récupérer les données
def get_cohorts():
    response = supabase.table("academics_cohort").select("*").execute()
    return response.data

# Insérer les données
def create_cohort(name, start_date, end_date):
    response = (
        supabase.table("academics_cohort")
        .insert({
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
        })
        .execute()
    )
    return response.data
```

### Exemple 2 : Utiliser Django ORM + Supabase

```python
# Django ORM marche normalement avec Supabase PostgreSQL
from academics.models import Cohort

# Récupérer tous les cohorts
cohorts = Cohort.objects.all()

# Créer un cohort
cohort = Cohort.objects.create(
    name="Japonais Niveau 1",
    start_date="2026-01-01",
    end_date="2026-03-01",
)

# Mettre à jour
cohort.name = "Nouvelle nom"
cohort.save()

# Supprimer
cohort.delete()
```

---

## 🚀 Démarrer l'application avec Supabase

```bash
# 1. Charger l'environnement
source .env  # Linux/Mac
# ou sur Windows: déjà chargé via python-dotenv

# 2. Lancer les migrations (si nécessaire)
python manage.py migrate

# 3. Démarrer le serveur
python manage.py runserver
```

---

## 🐛 Troubleshooting

### ❌ "could not connect to server"

**Vérifier :**
1. Votre password Supabase est correct
2. SSL mode est activé (`sslmode=require`)
3. Le host Supabase est accessible (xxx.supabase.co)

**Solution :**
```bash
# Tester la connexion
psql "postgresql://postgres:your_password@xxx.supabase.co:5432/postgres"
```

### ❌ "role 'postgres' does not exist"

✅ **Déjà résolu** - le dump SQL a été corrigé (yanis → postgres)

### ❌ "permission denied"

**Vérifier vos permissions dans Supabase :**
1. Allez à **Authentication** → **Users**
2. Vérifiez que votre utilisateur existe
3. Vérifiez les RLS policies dans **SQL Editor**

### ❌ "SSL certificate problem"

```python
# Si vous avez des problèmes SSL, ajouter à settings.py:
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
    'sslcert': '/path/to/cert.pem',  # si nécessaire
}
```

---

## 📊 Configuration avancée

### Connexion avec Pool

```python
# settings.py
if USE_SUPABASE:
    DATABASES['default']['CONN_MAX_AGE'] = 600  # Connection pooling
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'sslmode': 'require',
    }
```

### Migrations Django avec Supabase

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir l'état
python manage.py migrate --list
```

---

## ✅ Vérifier que tout fonctionne

```bash
python manage.py shell
```

```python
from django.db import connection
from academics.models import Cohort

# 1. Vérifier la connexion DB
print("Database:", connection.settings_dict['HOST'])

# 2. Compter les cohorts
print("Cohorts count:", Cohort.objects.count())

# 3. Récupérer le premier
first = Cohort.objects.first()
print("First cohort:", first.name if first else "No data")
```

---

## 📚 Ressources supplémentaires

- [Supabase Python Docs](https://supabase.com/docs/reference/python/introduction)
- [Django PostgreSQL Backend](https://docs.djangoproject.com/en/6.0/ref/databases/#postgresql-notes)
- [Supabase CLI](https://supabase.com/docs/guides/cli)

---

**✨ Vous êtes maintenant prêt à utiliser Supabase avec Django !**
