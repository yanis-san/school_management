# 💰 Guide : Modifier le Taux Horaire pour une Séance

## Overview

Vous pouvez maintenant modifier le taux horaire d'un professeur pour **une séance spécifique uniquement**, sans affecter :
- ✅ Son taux horaire général dans le cohort
- ✅ Les autres séances de ce prof
- ✅ Les séances des autres profs

## Comment ça fonctionne ?

### 1️⃣ Via l'Interface Web (Méthode Facile)

Allez sur la page de la séance : `http://127.0.0.1:8000/academics/session/{session_id}/`

Exemple : `http://127.0.0.1:8000/academics/session/2/`

#### Étapes :

1. **Repérez la section "Taux Horaire pour cette Séance"** (avec l'icône 💰)
   - Affiche le **taux standard du groupe**
   - Affiche le **taux actuellement utilisé**

2. **Remplissez le champ "Surcharge du taux horaire"**
   - Entrez le nouveau taux en DA/h
   - Exemple : 1000 (pour 1000 DA/h)

3. **Cliquez sur "Valider la Séance"**
   - Le taux est immédiatement appliqué à cette séance
   - Un message de confirmation s'affiche
   - La rémunération est recalculée

4. **Pour réinitialiser**, cliquez le bouton "Réinitialiser"
   - Le taux revient au taux standard du cohort

### 2️⃣ Via Django Admin

1. Allez sur `http://127.0.0.1:8000/admin/academics/coursesession/`

2. Cliquez sur la séance à modifier

3. Trouvez le champ **"Taux Horaire Spécifique (DA/h)"**
   - Laissez vide = utilise le taux du cohort
   - Remplissez = surcharge pour cette séance uniquement

4. Cliquez "Enregistrer"

### 3️⃣ Programmatiquement

```python
from academics.models import CourseSession

session = CourseSession.objects.get(id=2)

# Appliquer une surcharge
session.teacher_hourly_rate_override = 1000
session.save()

# Vérifier le taux utilisé
print(f"Taux standard : {session.cohort.teacher_hourly_rate} DA/h")
print(f"Taux override : {session.teacher_hourly_rate_override}")
print(f"Taux utilisé pour la paie : {session.pay_hourly_rate} DA/h")
print(f"Montant de la séance : {session.pay_amount} DA")

# Enlever la surcharge
session.teacher_hourly_rate_override = None
session.save()
```

## Priorité de Calcul

Le taux horaire utilisé pour la paie suit cette priorité :

1. **Override spécifique à la séance** (si rempli) ← 🎯 Plus haute priorité
2. **Tarif spécifique Ramadan** (si en période Ramadan et tarif défini)
3. **Tarif standard du cohort** ← Utilisé par défaut

## Exemples Concrets

### Exemple 1 : Prof avec surcharge unique

**Cohort "Japonais N1" :**
- Taux standard : 750 DA/h

**Séance 1 (normal) :**
- Taux utilisé : 750 DA/h
- 2h × 750 = 1500 DA

**Séance 2 (cours spécial) :**
- Override appliqué : 1200 DA/h
- Taux utilisé : 1200 DA/h
- 2h × 1200 = 2400 DA

**Séance 3 (normal) :**
- Taux utilisé : 750 DA/h
- 2h × 750 = 1500 DA

**Total : 1500 + 2400 + 1500 = 5400 DA**

### Exemple 2 : Ramadan + Override

**Cohort avec Ramadan :**
- Taux standard : 750 DA/h
- Taux Ramadan : 900 DA/h

**Séance pendant Ramadan (sans override) :**
- Taux utilisé : 900 DA/h (Ramadan)
- 2h × 900 = 1800 DA

**Séance pendant Ramadan (avec override 1100) :**
- Taux utilisé : 1100 DA/h (override > Ramadan)
- 2h × 1100 = 2200 DA

## Affichage dans les Rapports de Paie

Quand vous consultez les rapports de paie du professeur :

✅ Le taux horaire override est **automatiquement utilisé**
✅ Les montants calculés sont **exacts**
✅ Les overrides des séances **n'apparaissent pas dans le détail**, ils sont intégrés dans les calculs

## Notes Importantes

⚠️ **Pas d'effet rétroactif**
- Modifier le taux d'une séance déjà complétée nécessite de mettre à jour manuellement la rémunération du professeur

💡 **Traçabilité**
- Chaque modification laisse une trace dans les messages de la page
- Un badge orange 🔄 indique la présence d'une surcharge sur la séance

🔒 **Permissions**
- Les professeurs (is_teacher) voient les séances mais ne peuvent pas modifier les tarifs (pour éviter les conflits)
- Seul le staff/admin peut modifier les tarifs

## Dépannage

### Q: Le taux ne change pas ?
**R:** Vérifiez que vous avez cliqué "Valider la Séance". Le champ doit être rempli **avant** la validation.

### Q: Comment voir la surcharge dans l'admin ?
**R:** Dans la liste des séances (CourseSession), regardez la colonne "Taux Horaire" pour voir 🔄 SURCHARGE si applicable.

### Q: Peut-on modifier une séance complétée ?
**R:** Oui, en cliquant le bouton "✏️ Modifier" en bas de la page. Cela permet de corriger les tarifs après coup.

## Structure Technique

### Modèle

```python
class CourseSession(models.Model):
    # ...
    teacher_hourly_rate_override = models.IntegerField(
        null=True, blank=True,
        verbose_name="Taux Horaire Spécifique (DA/h)",
        help_text="Surcharge pour cette séance uniquement"
    )
    
    @property
    def pay_hourly_rate(self) -> int:
        """Taux utilisé pour la paie (override > Ramadan > standard)"""
        if self.teacher_hourly_rate_override is not None:
            return self.teacher_hourly_rate_override
        if self.is_ramadan and self.cohort.ramadan_teacher_hourly_rate:
            return self.cohort.ramadan_teacher_hourly_rate
        return self.cohort.teacher_hourly_rate
```

### Migration

Fichier : `academics/migrations/0013_coursesession_teacher_hourly_rate_override.py`

Appliquée automatiquement avec : `python manage.py migrate`
