# Guide d'Utilisation - Abréviation des Cohorts

## Vue d'ensemble

La méthode `get_abbreviation()` génère une abréviation compacte et structurée pour chaque cohort. C'est utile pour les rapports, les identifiants, les exports, etc.

## Format

```
[CODE_LANGUE][NIVEAU][MODALITE][ANNEE_MOIS]
```

### Exemples

| Cohort | Abréviation | Signification |
|--------|-------------|---------------|
| Chinois Niveau 3 (présentiel) - Jan 2026 | `CHN3P0126` | **CHN**=Chinois, **3**=Niveau 3, **P**=Présentiel, **0126**=Janvier 2026 |
| Japonais Niveau 6 (en ligne) - Jan 2026 | `JPN6O0126` | **JPN**=Japonais, **6**=Niveau 6, **O**=Online, **0126**=Janvier 2026 |
| Japonais Niveau 6 (individuel en ligne) - Jan 2026 | `JPN6IO0126` | **JPN**=Japonais, **6**=Niveau 6, **IO**=Individuel Online, **0126**=Janvier 2026 |
| Coréen Niveau 1 (individuel présentiel) - Jan 2026 | `KR1IP0126` | **KR**=Coréen, **1**=Niveau 1, **IP**=Individuel Présentiel, **0126**=Janvier 2026 |

## Codes de Modalité

| Modalité | Code | Signification |
|----------|------|---------------|
| Présentiel (groupe) | `P` | In-person Group |
| En ligne (groupe) | `O` | Online (Open) |
| Individuel Présentiel | `IP` | Individual In-Person |
| Individuel En ligne | `IO` | Individual Online |

## Codes de Langues (Extensible)

La liste complète est définie dans `LANGUAGE_CODES` (dans [academics/models.py](academics/models.py)):

- **Langues asiatiques**: CHN (Chinois), JPN (Japonais), KR (Coréen), THA (Thaï), VIE (Vietnamien), etc.
- **Langues européennes**: FRA (Français), ENG (Anglais), DEU (Allemand), ESP (Espagnol), etc.
- **Ateliers**: CALL (Calligraphie), PAINT (Peinture), DANCE (Danse), MUS (Musique), etc.

## Utilisation en Python

```python
from academics.models import Cohort

# Récupérer un cohort
cohort = Cohort.objects.first()

# Obtenir l'abréviation
abbr = cohort.get_abbreviation()
print(abbr)  # Exemple: "CHN3P0126"
```

## Utilisation en Template Django

```html
{% for cohort in cohorts %}
    <tr>
        <td>{{ cohort.name }}</td>
        <td>{{ cohort.get_abbreviation }}</td>
    </tr>
{% endfor %}
```

## Utilisation en Queryset (Annotation)

```python
from django.db.models import Value
from django.db.models.functions import Concat

cohorts = Cohort.objects.all().values('name', 'get_abbreviation')
```

## Ajouter une nouvelle langue/atelier

C'est très simple ! Il suffit d'ajouter une ligne au dictionnaire `LANGUAGE_CODES` dans [academics/models.py](academics/models.py):

```python
LANGUAGE_CODES = {
    'Chinois': 'CHN',
    'Japonais': 'JPN',
    'Coréen': 'KR',
    # Ajouter ici:
    'Nouvelle Langue': 'NLL',  # Code 3 lettres
    'Mon Atelier': 'ATEL',      # Code de 3-4 lettres
}
```

## Cas limites

- **Langue non trouvée**: Un code par défaut est généré (première 3 lettres du nom)
- **Niveau sans chiffre**: La valeur `0` est utilisée
- **Erreur lors de la génération**: Retourne `UNKNOWN_<ID>`

## Performance

- La méthode utilise un **cache interne** (`_abbreviation_cache`) pour éviter les recalculs
- Le cache est réinitialisé à chaque `save()` de l'objet Cohort

## Intégration avec d'autres modules

Vous pouvez utiliser l'abréviation pour:

- **Rapports**: Identifiants uniques dans les exports
- **Analytics**: Regroupement des données par abréviation
- **Exports**: Noms de fichiers (ex: `Effectif_JPN6IO0126.csv`)
- **API**: Identifiants plus courts et lisibles
- **Logs**: Traçabilité améliorée

---

**Fichier modifié**: [academics/models.py](academics/models.py)  
**Date d'ajout**: Janvier 2026
