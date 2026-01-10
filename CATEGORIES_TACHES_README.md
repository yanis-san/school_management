# 📁 Système de Catégories pour les Tâches

## 🎯 Objectif

Permettre d'organiser et de filtrer les tâches par catégorie pour une meilleure gestion.

## ✅ Fonctionnalités Implémentées

### 1. Modèle de Données

**Nouveau modèle `Category`** (tasks/models.py) :
- `name` : Nom unique de la catégorie (ex: "Urgent", "Finance", "Suivi Étudiant")
- `color` : Code couleur hexadécimal (ex: #EF4444) pour l'affichage visuel
- `description` : Description optionnelle de la catégorie
- `created_at` : Date de création automatique

**Modification du modèle `Task`** :
- Ajout d'une relation ForeignKey vers `Category` (optionnelle, nullable)
- Une tâche peut avoir zéro ou une catégorie
- Une catégorie peut contenir plusieurs tâches (relation `related_name='tasks'`)

### 2. Filtrage par Catégorie

**Dans la liste des tâches** ([tasks/](tasks/)) :
- Nouveau menu déroulant de filtrage par catégorie
- Filtre dynamique avec HTMX (pas de rechargement de page)
- Option "Toutes les catégories" pour voir toutes les tâches
- Le filtre se combine avec les filtres existants (statut, recherche)

**Vues mises à jour** :
- `task_list` : Accepte le paramètre `category` pour filtrer
- `task_toggle_complete` : Préserve le filtre de catégorie lors du marquage complet/incomplet
- `task_delete` : Préserve le filtre de catégorie lors de la suppression

### 3. Sélection de Catégorie

**Création de tâche** ([templates/tasks/task_create.html](templates/tasks/task_create.html)) :
- Nouveau champ "Catégorie" dans le formulaire
- Menu déroulant avec toutes les catégories disponibles
- Option "Aucune catégorie" (optionnel)

**Modification de tâche** ([templates/tasks/task_edit.html](templates/tasks/task_edit.html)) :
- Champ catégorie ajouté au formulaire d'édition
- La catégorie actuelle est pré-sélectionnée
- Possibilité de changer ou supprimer la catégorie

### 4. Affichage Visuel

**Badge de catégorie** :
- Affiché dans chaque carte de tâche
- Utilise la couleur définie dans la catégorie
- Format : 📁 [Nom de la catégorie]
- Style : Bordure et fond avec transparence basés sur la couleur

**Interface visuelle** :
```
📁 Finance
```
(Le badge utilise la couleur de la catégorie pour le fond et la bordure)

### 5. Interface d'Administration Django

**Gestion des catégories** (Django Admin) :
- Enregistrement de `Category` dans l'admin Django
- Liste affichant : nom, couleur, description, date de création
- Recherche par nom et description
- Tri par ordre alphabétique

**Amélioration de l'admin des tâches** :
- Ajout de `category` dans `list_display`
- Ajout de `category` dans `list_filter`
- Ajout de `category` dans le fieldset "Informations de la tâche"

## 📊 Catégories Pré-créées

8 catégories ont été créées par défaut via le script `create_categories.py` :

| Catégorie | Couleur | Description |
|-----------|---------|-------------|
| 🔴 Urgent | #EF4444 (Rouge) | Tâches urgentes nécessitant attention immédiate |
| 🔵 Suivi Étudiant | #3B82F6 (Bleu) | Tâches liées au suivi des étudiants |
| 🟢 Prospect | #10B981 (Vert) | Suivi des prospects et inscriptions |
| 🟠 Finance | #F59E0B (Orange) | Tâches liées aux paiements et finances |
| 🟣 Administratif | #6366F1 (Indigo) | Tâches administratives générales |
| 🟣 Inventaire | #8B5CF6 (Violet) | Gestion de l'inventaire |
| 🔴 Communication | #EC4899 (Rose) | Communication interne et externe |
| 🔵 Réunion | #14B8A6 (Teal) | Préparation et suivi de réunions |

## 🗂️ Fichiers Modifiés

### Modèles
- ✅ `tasks/models.py` : Ajout du modèle Category + relation Task->Category

### Vues
- ✅ `tasks/views.py` : 
  - Import de Category
  - Filtrage par catégorie dans task_list, task_toggle_complete, task_delete
  - Passage des catégories au contexte dans task_create et task_edit
  - Gestion du paramètre category dans le POST de création/édition

### Templates
- ✅ `templates/tasks/_tasks_section.html` : Menu déroulant de filtrage par catégorie
- ✅ `templates/tasks/task_create.html` : Champ de sélection de catégorie
- ✅ `templates/tasks/task_edit.html` : Champ de sélection de catégorie (édition)
- ✅ `templates/tasks/_task_list_partial.html` : Badge visuel de catégorie

### Administration
- ✅ `tasks/admin.py` : 
  - Enregistrement de CategoryAdmin
  - Ajout de category dans TaskAdmin

### Migrations
- ✅ `tasks/migrations/0002_category_task_category.py` : 
  - Création de la table Category
  - Ajout du champ category dans Task

### Scripts
- ✅ `create_categories.py` : Script pour créer les catégories d'exemple

## 🚀 Utilisation

### Pour l'utilisateur final :

1. **Créer une nouvelle catégorie** :
   - Aller dans l'admin Django : http://127.0.0.1:8000/admin/tasks/category/
   - Cliquer sur "Ajouter Category"
   - Remplir : nom, couleur (format #RRGGBB), description
   - Enregistrer

2. **Assigner une catégorie à une tâche** :
   - Lors de la création : sélectionner dans le menu "Catégorie"
   - Lors de l'édition : modifier le champ "Catégorie"

3. **Filtrer par catégorie** :
   - Dans la liste des tâches, utiliser le menu déroulant "Catégorie"
   - Sélectionner la catégorie souhaitée
   - La liste se met à jour automatiquement (HTMX)

### Pour le développeur :

1. **Ajouter de nouvelles catégories** :
```python
from tasks.models import Category

Category.objects.create(
    name="Ma Catégorie",
    color="#FF5733",
    description="Description de ma catégorie"
)
```

2. **Récupérer les tâches d'une catégorie** :
```python
category = Category.objects.get(name="Finance")
tasks = category.tasks.all()
```

3. **Assigner une catégorie à une tâche** :
```python
task = Task.objects.get(id=1)
category = Category.objects.get(name="Urgent")
task.category = category
task.save()
```

## 🔄 Prochaines Améliorations Possibles

1. **Statistiques par catégorie** :
   - Nombre de tâches par catégorie
   - Taux de complétion par catégorie

2. **Icônes personnalisées** :
   - Permettre d'assigner des emojis ou icônes aux catégories

3. **Sous-catégories** :
   - Hiérarchie de catégories parent/enfant

4. **Couleurs prédéfinies** :
   - Sélecteur de couleur avec palette pré-définie dans l'admin

5. **Badges multiples** :
   - Permettre plusieurs catégories par tâche (ManyToMany)

6. **Export par catégorie** :
   - Export Excel/PDF filtré par catégorie

## 🎨 Code Couleurs Recommandées

Pour maintenir une cohérence visuelle, voici des couleurs Tailwind CSS recommandées :

| Couleur | Hex | Utilisation suggérée |
|---------|-----|----------------------|
| Rouge | #EF4444 | Urgent, Critique |
| Orange | #F59E0B | Avertissement, Finance |
| Jaune | #F59E0B | En attente, À vérifier |
| Vert | #10B981 | Succès, Prospect, Validé |
| Bleu | #3B82F6 | Information, Suivi |
| Indigo | #6366F1 | Administratif |
| Violet | #8B5CF6 | Créatif, Inventaire |
| Rose | #EC4899 | Communication, Marketing |
| Teal | #14B8A6 | Réunion, Événement |

## 📝 Notes Techniques

- **Migration automatique** : Les tâches existantes auront `category=NULL` (aucune catégorie)
- **Suppression de catégorie** : Si une catégorie est supprimée, les tâches associées perdront leur catégorie (SET_NULL)
- **Performance** : Les requêtes utilisent `select_related()` pour optimiser les accès à la catégorie
- **HTMX** : Les filtres sont coordonnés via `hx-include` pour préserver tous les paramètres

## ✅ Tests Effectués

- ✅ Création de catégories via script
- ✅ Migrations appliquées sans erreur
- ✅ Serveur démarre sans erreur
- ✅ Admin Django affiche correctement les catégories
- ✅ Formulaire de création inclut le sélecteur de catégorie
- ✅ Formulaire d'édition inclut le sélecteur de catégorie
- ✅ Badge de catégorie s'affiche dans les cartes de tâche
- ✅ Filtre par catégorie dans la liste des tâches

## 🆘 Support

Pour toute question ou problème :
1. Vérifier que les migrations sont appliquées : `python manage.py migrate`
2. Vérifier que les catégories existent : `python create_categories.py`
3. Consulter les logs du serveur Django
4. Vérifier la console du navigateur pour les erreurs HTMX

---

**Date d'implémentation** : 10 janvier 2026  
**Version** : 1.0  
**Développeur** : Système de gestion scolaire
