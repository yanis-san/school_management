# 📅 Fonctionnalité Date Planifiée (Scheduled Date) - Documentation

## Vue d'ensemble
Cette fonctionnalité permet d'ajouter une **date planifiée** pour chaque tâche, distincte de la **date limite (deadline)**. Cela permet une meilleure planification quotidienne des tâches.

## Différences entre les dates

### 📅 Date planifiée (scheduled_date)
- **Signification** : "Je prévois de faire cette tâche ce jour-là"
- **Usage** : Planification quotidienne, organisation du travail
- **Flexibilité** : Peut être modifiée facilement selon les besoins
- **Optionnelle** : Peut être laissée vide

### ⏰ Date limite (deadline)
- **Signification** : "Cette tâche DOIT être terminée avant cette date"
- **Usage** : Date butoir absolue, non négociable
- **Contrainte** : Date ferme, dépassement = retard
- **Optionnelle** : Peut être laissée vide

### ➕ Date de création (created_at)
- **Signification** : Date à laquelle la tâche a été créée
- **Usage** : Historique, traçabilité
- **Automatique** : Remplie automatiquement par le système

## Modifications apportées

### 1. Modèle (models.py)
```python
scheduled_date = models.DateField(
    "Date planifiée",
    null=True,
    blank=True,
    help_text="Date à laquelle cette tâche doit être faite"
)
```

### 2. Migrations
- **Fichier** : `tasks/migrations/0003_task_scheduled_date_alter_task_deadline.py`
- **Statut** : ✅ Créée et appliquée avec succès

### 3. Formulaires
#### Création (task_create.html)
- Nouveau champ "Date planifiée" entre Priorité et Deadline
- Disposition en grille 3 colonnes : Priorité | Date planifiée | Deadline
- Pré-remplissage possible via URL : `?scheduled_date=2026-01-15`

#### Édition (task_edit.html)
- Même disposition que création
- Valeur pré-remplie avec `task.scheduled_date`

### 4. Vues (views.py)
#### task_create
- Récupère `scheduled_date` depuis POST
- Passe au `Task.objects.create()`
- Supporte pré-remplissage via GET parameter `?scheduled_date=YYYY-MM-DD`

#### task_edit
- Récupère et sauvegarde `scheduled_date` lors de la mise à jour

#### task_calendar
- Affiche les tâches selon leur `scheduled_date` en priorité
- Organisation : scheduled > deadline > created

#### tasks_by_day (NOUVEAU)
- **URL** : `/tasks/calendar/<year>/<month>/<day>/`
- Affiche toutes les tâches d'une date spécifique
- 3 sections :
  - Tâches planifiées ce jour
  - Tâches avec deadline ce jour
  - Tâches créées ce jour
- Navigation : jour précédent / jour suivant
- Statistiques par type

### 5. Templates

#### calendar.html
- **Jours cliquables** : Lien vers `tasks_by_day`
- **Symboles mis à jour** :
  - 📅 = Date planifiée
  - ⏰ = Deadline
  - ➕ = Date de création
- **Légende** : Mise à jour avec les 3 symboles

#### day_detail.html (NOUVEAU)
- Affiche toutes les tâches d'un jour spécifique
- Navigation entre jours
- Statistiques (total, planifiées, deadline, créées)
- Bouton "Créer une tâche pour ce jour" avec date pré-remplie

#### _task_card.html (NOUVEAU)
- Carte de tâche réutilisable
- Affiche dates selon contexte (show_scheduled, show_deadline, show_created)
- Actions : Éditer, Supprimer, Compléter
- Badges colorés par priorité

#### _task_list_partial.html
- **Date planifiée affichée** : Badge bleu avec emoji 📅
- **Mise en évidence** :
  - Rouge gras : Date planifiée dépassée
  - Bleu gras : Date planifiée aujourd'hui
  - Bleu normal : Date planifiée future

### 6. Admin
- `scheduled_date` ajouté à :
  - `list_display` : Visible dans la liste
  - `list_filter` : Filtrable
  - `fieldsets` : Dans la section "Informations de la tâche"

## Flux d'utilisation

### Créer une tâche avec date planifiée
1. Aller sur "Tâches" > "Créer une nouvelle tâche"
2. Remplir le titre
3. **Définir la date planifiée** : "Je vais faire ça le 15 janvier"
4. **Optionnel** : Définir la deadline : "Mais ça doit être fini avant le 20 janvier"
5. Enregistrer

### Depuis le calendrier
1. Aller sur "Calendrier Tâches"
2. Cliquer sur un jour (ex: 15 janvier)
3. Voir toutes les tâches de ce jour
4. Cliquer sur "Créer une tâche pour ce jour"
5. La date planifiée est automatiquement remplie avec le 15 janvier

### Consulter les tâches d'un jour
1. Calendrier > Cliquer sur un jour
2. Voir 3 sections :
   - **📅 Planifiées** : Tâches à faire ce jour
   - **⏰ Deadline** : Tâches qui doivent être finies ce jour
   - **➕ Créées** : Tâches créées ce jour
3. Naviguer entre jours avec les flèches

## Avantages

### Pour la planification quotidienne
- **Vue claire** de ce qui doit être fait chaque jour
- **Distinction** entre travail prévu et deadline finale
- **Flexibilité** pour reprogrammer sans stress

### Pour le calendrier
- **Visualisation** des tâches par jour
- **Clics directs** sur les jours pour voir détails
- **Navigation** fluide entre les jours

### Pour la gestion
- **3 perspectives temporelles** :
  - Quand créée (created_at)
  - Quand prévu de faire (scheduled_date)
  - Quand doit être fini (deadline)

## Exemples concrets

### Exemple 1 : Tâche simple
```
Titre: Appeler M. Dupont
Date planifiée: 15/01/2026 (je vais l'appeler lundi)
Deadline: 20/01/2026 (je dois l'avoir appelé avant vendredi)
```

### Exemple 2 : Tâche urgente
```
Titre: Préparer documents inscription
Date planifiée: 10/01/2026 (aujourd'hui)
Deadline: 10/01/2026 (aujourd'hui aussi - urgent!)
```

### Exemple 3 : Tâche flexible
```
Titre: Mettre à jour les contacts
Date planifiée: (vide - je ferai quand j'ai le temps)
Deadline: 31/01/2026 (mais avant fin du mois)
```

## Tests à effectuer

### ✅ Créer une tâche avec date planifiée
- [ ] Formulaire affiche bien les 3 colonnes
- [ ] Date planifiée se sauvegarde
- [ ] Apparaît dans la liste avec badge bleu

### ✅ Calendrier
- [ ] Tâches planifiées apparaissent sur le bon jour avec 📅
- [ ] Tâches deadline apparaissent avec ⏰
- [ ] Tâches créées apparaissent avec ➕
- [ ] Jours sont cliquables

### ✅ Vue jour
- [ ] Cliquer sur jour ouvre day_detail
- [ ] 3 sections affichées correctement
- [ ] Navigation précédent/suivant fonctionne
- [ ] Statistiques correctes

### ✅ Édition
- [ ] Modifier date planifiée fonctionne
- [ ] Date s'affiche correctement dans le formulaire

### ✅ Admin
- [ ] scheduled_date visible dans liste
- [ ] Filtrage par scheduled_date fonctionne

## Fichiers modifiés

### Modèle & Migrations
- `tasks/models.py` - Ajout champ scheduled_date
- `tasks/migrations/0003_task_scheduled_date_alter_task_deadline.py` - ✅ Appliquée

### Vues
- `tasks/views.py` - task_create, task_edit, task_calendar, tasks_by_day

### URLs
- `tasks/urls.py` - Ajout route day_detail

### Templates
- `templates/tasks/task_create.html` - Formulaire 3 colonnes
- `templates/tasks/task_edit.html` - Formulaire avec scheduled_date
- `templates/tasks/calendar.html` - Jours cliquables, légende mise à jour
- `templates/tasks/day_detail.html` - NOUVEAU
- `templates/tasks/_task_card.html` - NOUVEAU
- `templates/tasks/_task_list_partial.html` - Badge date planifiée

### Admin
- `tasks/admin.py` - scheduled_date dans list_display et fieldsets

## Script utile

### apply_tasks_migration.py
Script pour créer et appliquer les migrations automatiquement.
```bash
python apply_tasks_migration.py
```

## Date de mise en œuvre
**10 janvier 2026**

## Statut
✅ **Fonctionnalité complète et opérationnelle**

---

*Cette fonctionnalité améliore considérablement la gestion quotidienne des tâches en séparant la planification (quand je vais le faire) de la contrainte (quand ça doit être fini).*
