#!/usr/bin/env python3
"""
QUICK REFERENCE - Supabase avec Django
Aide-mémoire rapide des commandes essentielles
"""

# ═══════════════════════════════════════════════════════════════════════════
# 🎯 CONFIGURATION INITIALE
# ═══════════════════════════════════════════════════════════════════════════

"""
1. Récupérez vos identifiants Supabase:
   - Allez à https://app.supabase.com
   - Sélectionnez votre projet
   - Settings → Database → Connection Info

2. Lancez la configuration:
   python setup_supabase.py

3. Vérifiez:
   python test_supabase_connection.py

4. Démarrez:
   python manage.py runserver
"""

# ═══════════════════════════════════════════════════════════════════════════
# 🔄 BASCULER ENTRE LOCAL ET SUPABASE
# ═══════════════════════════════════════════════════════════════════════════

"""
Dans votre fichier .env :

✅ UTILISER SUPABASE:
   USE_SUPABASE=true
   SUPABASE_DB_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres

✅ UTILISER LOCAL:
   USE_SUPABASE=false
"""

# ═══════════════════════════════════════════════════════════════════════════
# 💻 UTILISER DJANGO ORM (Identique pour local et Supabase)
# ═══════════════════════════════════════════════════════════════════════════

from academics.models import Cohort
from students.models import Student

# Récupérer tous
cohorts = Cohort.objects.all()

# Récupérer un
cohort = Cohort.objects.get(id=1)

# Créer
new_cohort = Cohort.objects.create(
    name="Japonais Niveau 1",
    start_date="2026-01-01",
    end_date="2026-03-01",
)

# Mettre à jour
cohort.name = "Nouveau nom"
cohort.save()

# Supprimer
cohort.delete()

# Compter
count = Cohort.objects.count()

# Filtrer
cohorts = Cohort.objects.filter(name__contains="Japonais")

# ═══════════════════════════════════════════════════════════════════════════
# 🚀 UTILISER SUPABASE CLIENT (Pour opérations avancées)
# ═══════════════════════════════════════════════════════════════════════════

from supabase_utils import SupabaseManager

# ℹ️ Vérifier la configuration
is_supabase = SupabaseManager.is_using_supabase()
db_info = SupabaseManager.get_db_info()

# ✅ Sélectionner
cohorts = SupabaseManager.select_all('academics_cohort')
cohort = SupabaseManager.select_one('academics_cohort', 'id', 1)

# ✅ Insérer
new_cohort = SupabaseManager.insert('academics_cohort', {
    'name': 'Nouveau Cohort',
    'start_date': '2026-01-01',
    'end_date': '2026-03-01',
})

# ✅ Mettre à jour
updated = SupabaseManager.update('academics_cohort', 'id', 1, {
    'name': 'Nom Modifié'
})

# ✅ Supprimer
SupabaseManager.delete('academics_cohort', 'id', 1)

# ═══════════════════════════════════════════════════════════════════════════
# 🔍 VÉRIFICATIONS ET TESTS
# ═══════════════════════════════════════════════════════════════════════════

# Ouvrir Django Shell
"""
python manage.py shell
"""

# Dans Django shell:
from django.db import connection
from supabase_utils import SupabaseManager

# Vérifier la connexion
db_info = SupabaseManager.get_db_info()
print(db_info)

# Vérifier les données
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM academics_cohort;")
print(f"Cohorts: {cursor.fetchone()[0]}")

# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ COMMANDES DJANGO UTILES
# ═══════════════════════════════════════════════════════════════════════════

"""
# Appliquer les migrations
python manage.py migrate

# Créer un super utilisateur
python manage.py createsuperuser

# Shell interactif
python manage.py shell

# Voir l'état des migrations
python manage.py migrate --list

# Test de connexion
python test_supabase_connection.py

# Setup Supabase
python setup_supabase.py
"""

# ═══════════════════════════════════════════════════════════════════════════
# 📁 FICHIERS IMPORTANTS
# ═══════════════════════════════════════════════════════════════════════════

"""
.env                              - Configuration (à remplir)
.env.example                      - Template de configuration
config/settings.py               - Configuration Django
supabase_utils.py               - Manager Supabase
test_supabase_connection.py      - Test de connexion
setup_supabase.py                - Configuration interactive
GUIDE_SUPABASE_DJANGO.md        - Guide complet
README_SUPABASE.md              - Quick start
"""

# ═══════════════════════════════════════════════════════════════════════════
# 🚨 TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════════════════════

"""
❌ "could not connect to server"
✅ Vérifiez: password, host, port, SSL mode

❌ "role 'postgres' does not exist"
✅ Le dump SQL a été corrigé automatiquement

❌ "permission denied"
✅ Vérifiez les RLS policies dans Supabase

❌ Django n'utilise pas Supabase
✅ Vérifiez: USE_SUPABASE=true dans .env
✅ Redémarrez le serveur Django
"""

# ═══════════════════════════════════════════════════════════════════════════
# ✨ VOUS ÊTES PRÊT!
# ═══════════════════════════════════════════════════════════════════════════

print("""
🎉 Configuration Supabase terminée!

Prochaines étapes:
1. python test_supabase_connection.py
2. python manage.py runserver
3. Allez à http://localhost:8000

Documentation complète: GUIDE_SUPABASE_DJANGO.md
Quick start: README_SUPABASE.md
""")
