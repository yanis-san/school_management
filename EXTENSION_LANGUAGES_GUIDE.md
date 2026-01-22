# Guide d'Extension - Ajouter des Langues/Ateliers

## Comment ajouter une nouvelle langue ou un nouvel atelier

C'est très facile ! Voici les 3 étapes :

### Étape 1: Localiser le dictionnaire

Ouvrez le fichier [academics/models.py](academics/models.py) et trouvez le dictionnaire `LANGUAGE_CODES` au début du fichier:

```python
LANGUAGE_CODES = {
    'Chinois': 'CHN',
    'Mandarin': 'CHN',
    'Cantonais': 'CAN',
    'Japonais': 'JPN',
    'Coréen': 'KR',
    # ... etc
}
```

### Étape 2: Ajouter votre entrée

Ajoutez une nouvelle ligne avec le format:

```python
'Nom Exact de la Langue': 'CODE',
```

**Conventions:**
- **Code pour langues**: 3 lettres (ISO 639-3) en majuscules
  - Exemples: `'Français': 'FRA'`, `'Anglais': 'ENG'`, `'Allemand': 'DEU'`
  
- **Code pour ateliers**: 4+ lettres descriptives en majuscules
  - Exemples: `'Calligraphie': 'CALL'`, `'Peinture': 'PAINT'`

### Étape 3: Valider

Redémarrez le serveur Django et testez :

```python
python manage.py shell
from academics.models import Cohort, Subject, Level

# Créer un Subject avec la nouvelle langue
subject = Subject.objects.create(name='Nouvelle Langue')
# Créer un Cohort et vérifier l'abréviation
cohort = Cohort(subject=subject, ...)
print(cohort.get_abbreviation())  # Doit contenir votre code
```

---

## Exemples concrets

### Exemple 1: Ajouter le Turc

**Avant:**
```python
LANGUAGE_CODES = {
    'Chinois': 'CHN',
    'Japonais': 'JPN',
}
```

**Après:**
```python
LANGUAGE_CODES = {
    'Chinois': 'CHN',
    'Japonais': 'JPN',
    'Turc': 'TUR',  # ✨ Nouvelle ligne
}
```

**Résultat:**
```
Turc Niveau 2 (présentiel) - Jan 2026 → TUR2P0126
```

---

### Exemple 2: Ajouter la Calligraphie Arabe comme atelier

**Avant:**
```python
LANGUAGE_CODES = {
    'Chinois': 'CHN',
    'Calligraphie': 'CALL',
}
```

**Après:**
```python
LANGUAGE_CODES = {
    'Chinois': 'CHN',
    'Calligraphie': 'CALL',
    'Calligraphie Arabe': 'CALAR',  # ✨ Nouvelle ligne
}
```

**Résultat:**
```
Calligraphie Arabe Niveau 1 (présentiel) - Jan 2026 → CALAR1P0126
```

---

### Exemple 3: Ajouter le Coréen avec variante

**Avant:**
```python
LANGUAGE_CODES = {
    'Coréen': 'KR',
}
```

**Après:**
```python
LANGUAGE_CODES = {
    'Coréen': 'KR',
    'Coréen Moderne': 'KRM',  # ✨ Variante moderne
    'Coréen Classique': 'KRC',  # ✨ Variante classique
}
```

**Résultat:**
```
Coréen Moderne Niveau 1 (présentiel) - Jan 2026 → KRM1P0126
Coréen Classique Niveau 1 (présentiel) - Jan 2026 → KRC1P0126
```

---

## Bonnes pratiques

✅ **À FAIRE:**
- Utiliser des codes courts (2-4 lettres)
- Respecter le nom exact du `Subject` dans Django
- Ajouter les variantes si nécessaire
- Laisser des commentaires pour les codes obscurs

❌ **À ÉVITER:**
- Utiliser des accents: `'Français'` ✓ pas `'Françíès'` ✗
- Changer les codes existants (risque de confusion)
- Ajouter des espaces dans les codes: `'CHN 3'` ✗
- Utiliser des codes trop longs (>5 lettres)

---

## Vue d'ensemble complète

Pour voir tous les codes disponibles:

```bash
python manage.py shell
from academics.models import LANGUAGE_CODES
for lang, code in sorted(LANGUAGE_CODES.items()):
    print(f"{code:6} → {lang}")
```

---

## Questions fréquentes

### Q: Je veux ajouter une langue qui a plusieurs variantes (Standard, Moderne, etc.)
**R:** Créez plusieurs entrées:
```python
'Arabe': 'ARA',
'Arabe Standard': 'ARAS',
'Arabe Égyptien': 'ARAE',
'Arabe Marocain': 'ARAM',
```

### Q: Puis-je utiliser le même code pour plusieurs langues?
**R:** ❌ Non, chaque langue doit avoir un code unique. Sinon il y aura confusion.

### Q: Que se passe-t-il si je change un code existant?
**R:** Les anciennes abréviations (déjà générées) restent inchangées. Seules les nouvelles abréviations utiliseront le nouveau code.

### Q: Comment voir si une langue est déjà ajoutée?
**R:** Utilisez le shell Django:
```python
from academics.models import LANGUAGE_CODES
'Turc' in LANGUAGE_CODES  # True ou False
```

---

## Support

Pour toute question ou si vous trouvez un bug, consultez:
- [COHORT_ABBREVIATION_GUIDE.md](COHORT_ABBREVIATION_GUIDE.md)
- [academics/models.py](academics/models.py)
- Script de test: [test_cohort_abbreviation.py](test_cohort_abbreviation.py)
