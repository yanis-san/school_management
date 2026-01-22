"""
OPTIONNEL: Si vous voulez persister l'abréviation en base de données.

ATTENTION: La méthode get_abbreviation() fonctionne SANS ajouter de champ à la base.
Ce fichier est fourni SEULEMENT si vous voulez optimiser les performances en persistant l'abréviation.

Cas d'usage pour persister l'abréviation:
- 📊 Vous faites beaucoup de requêtes/exports
- 🔍 Vous voulez chercher par abréviation rapidement
- 🗄️ Vous voulez l'historique des abréviations
- 📈 Vous avez 10000+ cohorts

Si vous ne faites pas ça, l'abréviation actuelle fonctionne PARFAITEMENT.
"""

# ============================================================================
# OPTION 1: AJOUTER UN CHAMP OPTIONNEL (Recommandé si besoin)
# ============================================================================

"""
ÉTAPE 1: Modifier models.py

Dans academics/models.py, ajouter ce champ à la classe Cohort:

class Cohort(models.Model):
    # ... champs existants ...
    
    # NOUVEAU (optionnel):
    abbreviation = models.CharField(
        max_length=20,
        blank=True,
        editable=False,  # Généré automatiquement
        db_index=True,   # Index pour les recherches rapides
        unique=True,
        help_text="Abréviation unique du cohort (généré automatiquement)"
    )
"""

# ============================================================================
# ÉTAPE 2: Créer la migration
# ============================================================================

"""
Depuis le terminal:

python manage.py makemigrations academics
python manage.py migrate
"""

# ============================================================================
# ÉTAPE 3: Mettre à jour la méthode save()
# ============================================================================

"""
Modifier la méthode save() de Cohort:

def save(self, *args, **kwargs):
    # Réinitialiser le cache
    self._abbreviation_cache = None
    
    # Assigner l'année académique active si non fournie
    if self.academic_year is None:
        current = AcademicYear.get_current()
        if current is not None:
            self.academic_year = current
    
    # Générer le nom normalisé
    self.name = self.generate_name()
    
    # NOUVEAU: Persister l'abréviation
    self.abbreviation = self.get_abbreviation()
    
    super().save(*args, **kwargs)
"""

# ============================================================================
# ÉTAPE 4: Utiliser l'abréviation en base de données
# ============================================================================

"""
Après migration, vous pouvez:

# Recherche rapide
cohort = Cohort.objects.get(abbreviation='CHN3P0126')

# Filtres
cohorts = Cohort.objects.filter(abbreviation__startswith='JPN')

# Rapports rapides
Cohort.objects.filter(abbreviation__contains='O0126')  # Tous les online en Jan 2026
"""

# ============================================================================
# OPTION 2: CHARGER LES ABRÉVIATIONS EXISTANTES
# ============================================================================

"""
Si vous avez déjà des cohorts, créez une migration pour les remplir:

python manage.py makemigrations academics --empty populate_abbreviations
"""

# Fichier migration généré (0XXX_populate_abbreviations.py):

from django.db import migrations
from academics.models import Cohort

def populate_abbreviations(apps, schema_editor):
    """Remplir le champ abbreviation pour tous les cohorts existants."""
    Cohort_model = apps.get_model('academics', 'Cohort')
    
    for cohort in Cohort_model.objects.all():
        # On ne peut pas utiliser get_abbreviation() dans la migration
        # Il faut recréer la logique ici
        
        # Alternative 1: Charger depuis Django
        from academics.models import LANGUAGE_CODES, MODALITY_CODES
        
        subject_name = cohort.subject.name.strip()
        language_code = LANGUAGE_CODES.get(subject_name, subject_name[:3].upper())
        
        level_name = cohort.level.name.strip()
        level_number = ''.join(c for c in level_name if c.isdigit()) or '0'
        
        modality_key = (cohort.modality, cohort.is_individual)
        modality_code = MODALITY_CODES.get(modality_key, 'X')
        
        year_short = str(cohort.start_date.year)[-2:]
        month_zero = f"{cohort.start_date.month:02d}"
        date_code = year_short + month_zero
        
        abbreviation = f"{language_code}{level_number}{modality_code}{date_code}"
        
        cohort.abbreviation = abbreviation
        cohort.save()

def reverse_abbreviations(apps, schema_editor):
    """Vider le champ abbreviation."""
    Cohort_model = apps.get_model('academics', 'Cohort')
    Cohort_model.objects.all().update(abbreviation='')

class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0XX_previous_migration'),  # À adapter
    ]

    operations = [
        migrations.RunPython(populate_abbreviations, reverse_abbreviations),
    ]


# ============================================================================
# ÉTAPE 5: Mettre à jour l'admin
# ============================================================================

"""
Dans academics/admin.py, ajouter 'abbreviation' à la liste:

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'abbreviation',  # NOUVEAU
        'subject',
        'level',
        # ...
    ]
    
    search_fields = [
        'name',
        'abbreviation',  # NOUVEAU - chercher par abréviation
        'subject__name',
    ]
    
    readonly_fields = [
        'name',
        'abbreviation',  # NOUVEAU - généré automatiquement
    ]
"""

# ============================================================================
# COMPARAISON: AVEC VS SANS PERSISTANCE
# ============================================================================

"""
┌────────────────────────────────────────────────────────────────────────────┐
│                     AVEC PERSISTANCE          │    SANS (actuel)          │
├────────────────────────────────────────────────────────────────────────────┤
│ ✅ Recherche par abréviation O(1)              │ ❌ Recherche O(n)        │
│ ✅ Index en base de données                    │ ❌ Pas d'index           │
│ ✅ Visualiser en admin facilement              │ ⚠️ Appel de méthode      │
│ ✅ Historique possible                         │ ❌ Recalcul chaque fois  │
│ ❌ Champ supplémentaire en base                │ ✅ Aucune base ajoutée   │
│ ❌ Migration à faire                           │ ✅ Rien à faire          │
│ ⚠️ Risque de synchronisation                   │ ✅ Toujours à jour       │
│                                                 │                           │
│ RECOMMANDÉ pour: >1000 cohorts, requêtes      │ RECOMMANDÉ pour: <100   │
│ fréquentes, exports massifs                    │ cohorts, usage simple   │
└────────────────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# SCRIPT DE TEST COMPARATIF
# ============================================================================

"""
Pour tester la performance:

import time
from academics.models import Cohort

# Test 1: Sans persistance (actuel)
start = time.time()
for _ in range(1000):
    cohort = Cohort.objects.first()
    abbr = cohort.get_abbreviation()
end = time.time()
print(f"Sans persistance: {end - start:.3f}s pour 1000 appels")

# Test 2: Avec persistance (après migration)
start = time.time()
for _ in range(1000):
    cohort = Cohort.objects.get(abbreviation='CHN3P0126')
end = time.time()
print(f"Avec persistance: {end - start:.3f}s pour 1000 requêtes")
"""

# ============================================================================
# CONCLUSION
# ============================================================================

"""
RECOMMANDATION:

1. ✅ Pour maintenant: Utiliser get_abbreviation() (SANS persistance)
   - Aucune migration nécessaire
   - Méthode performante avec cache
   - Simple et flexible

2. ⏱️ Plus tard: Persister si besoin (voir options ci-dessus)
   - Quand vous avez 1000+ cohorts
   - Quand vous faites beaucoup de recherches
   - Quand vous exportez massivementCe fichier reste ici pour référence future. Vous n'en avez PAS besoin maintenant !
"""
