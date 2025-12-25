# 📦 App Inventaire - Documentation Complète

## 🎯 Vue d'ensemble

L'app **Inventaire** est un système complet de gestion des stocks, des articles et des listes d'achat. Elle permet de :

- ✅ Gérer les articles en inventaire par catégories
- ✅ Suivre les quantités et les niveaux de stock
- ✅ Créer et gérer les listes d'achat pour des événements
- ✅ Générer des PDF et exporter les listes
- ✅ Suivre les achats et les coûts
- ✅ Alertes automatiques pour stock faible/rupture

---

## 📊 Structure de la Base de Données

### 1. **ItemCategory** - Catégories d'articles
```python
- name: str - Nom unique de la catégorie
- description: text - Description
- color: str - Couleur hex pour le visuel (#RRGGBB)
- created_at: datetime - Date de création
```

**Exemples:** Fournitures scolaires, Nettoyage, Équipement, etc.

### 2. **InventoryItem** - Articles en inventaire
```python
- name: str - Nom de l'article
- category: ForeignKey → ItemCategory
- description: text - Description détaillée
- quantity_current: int - Quantité disponible actuellement
- quantity_min: int - Quantité minimale (alerte si inférieure)
- unit: str - Unité (pièce, boîte, kg, litre, etc.)
- purchase_price: decimal - Prix d'achat (€)
- location: str - Où est stocké l'article
- is_mandatory: bool - Article obligatoire (🔴 flag)
- status: choice - Statut auto-calculé:
  * in_stock (✅)
  * low_stock (⚠️)
  * out_of_stock (❌)
  * order_pending (📦)
- notes: text - Notes additionnelles
```

**Auto-mise à jour du statut:**
- `quantity_current == 0` → `out_of_stock`
- `quantity_current <= quantity_min` → `low_stock`
- Sinon → `in_stock`

### 3. **ShoppingList** - Listes d'achat
```python
- title: str - Titre de la liste
- description: text - Description
- created_by: ForeignKey → User
- event_date: date - Date de l'événement
- status: choice:
  * draft (📝)
  * in_progress (🔄)
  * completed (✅)
- total_cost: decimal - Coût total (auto-calculé)
- created_at: datetime
- updated_at: datetime
```

**Auto-calcul du coût:** Somme de `quantity_needed * unit_price` pour tous les articles

### 4. **ShoppingListItem** - Éléments d'une liste
```python
- shopping_list: ForeignKey → ShoppingList
- item: ForeignKey → InventoryItem (nullable)
- custom_item_name: str - Nom personnalisé si pas lié à un article
- quantity_needed: decimal - Quantité à acheter
- unit: str - Unité
- unit_price: decimal - Prix unitaire (€)
- priority: int (1-5) - Niveau de priorité
- supplier: str - Fournisseur optionnel
- notes: text - Notes spécifiques
- is_purchased: bool - Marqué comme acheté
- purchase_date: date - Date d'achat
```

**Méthodes:**
- `get_item_name()` - Retourne le nom (custom ou de l'article)
- `get_total_price()` - Calcule `quantity_needed * unit_price`
- `get_priority_display()` - Affiche le niveau 1-5

---

## 🎨 Interface Utilisateur

### Dashboard (`/inventory/`)
- 📊 Statistiques: Total articles, Stock OK, Stock faible, Ruptures
- 🚨 Articles critiques (obligatoires et problématiques)
- ⚠️ Articles à surveiller (stock faible)
- 🛒 Listes d'achat récentes

### Articles (`/inventory/items/`)
- 📋 Liste complète des articles
- 🔍 Filtres: par catégorie, statut, articles obligatoires
- 📊 Tableau avec code couleur par statut
- ✎ Accès direct aux éditions admin

### Listes d'achat (`/inventory/shopping-lists/`)
- 🛒 Grille de listes d'achat
- 📅 Dates d'événement
- 💰 Coûts totaux
- 📊 Statut de progression
- 🔗 Actions: Voir, PDF, Éditer

### Détail Liste (`/inventory/shopping-list/<id>/`)
- ✅ Barre de progression (achats complétés)
- 📝 Infos: créateur, date, description
- 📊 Articles avec cases à cocher pour marquer comme acheté
- 🔄 Mise à jour en temps réel (AJAX)
- 💰 Coûts individuels et total
- 📄 Export PDF et texte

---

## 🔧 Fonctionnalités Principales

### 1. Gestion des Articles
```bash
# Via Admin Django ou code:
InventoryItem.objects.create(
    name="Cahiers A4",
    category=category,
    quantity_current=50,
    quantity_min=20,
    unit="pcs",
    is_mandatory=True
)
```

**Statut auto-mis à jour** lors de chaque `save()`

### 2. Gestion des Listes d'Achat
```bash
# Créer une liste
shopping_list = ShoppingList.objects.create(
    title="Achat rentrée",
    created_by=user,
    event_date="2024-09-01",
    status="draft"
)

# Ajouter des articles
ShoppingListItem.objects.create(
    shopping_list=shopping_list,
    item=inventory_item,
    quantity_needed=10,
    unit_price=2.50,
    priority=1
)

# Coût total auto-calculé après ajout
shopping_list.update_total_cost()
```

### 3. Export PDF
- 📄 Format A4 paysage professionnel
- 📊 Tableau avec tous les détails
- 📋 Statut "acheté/à acheter" pour chaque item
- 💰 Coût total et résumé

### 4. Export Texte
- 📝 Format texte pour copier-coller facilement
- 📋 Tous les détails (priorité, fournisseur, notes)
- 🔗 Lien de accès vers la liste en ligne

### 5. Suivi des Achats
- ✅ Marquer les articles comme achetés
- 📅 Date d'achat enregistrée
- 🔄 Progression en temps réel (AJAX)

---

## 🔐 Permissions

Seuls les **admins** (non-professeurs) peuvent accéder à :
- Dashboard inventaire
- Liste des articles
- Listes d'achat
- Édition via admin

**Vérification:** `user.is_authenticated and not user.is_teacher`

---

## 🚀 Commandes de Management

### Créer les données de test
```bash
python manage.py seed_inventory
```

Crée automatiquement:
- 5 catégories pré-remplies
- 10 articles de test
- 2 listes d'achat exemple

---

## 📱 API & URLs

### Vues disponibles
| URL | Vue | Permission |
|-----|-----|-----------|
| `/inventory/` | Dashboard | Admin |
| `/inventory/items/` | Liste articles | Admin |
| `/inventory/shopping-lists/` | Listes d'achat | Admin |
| `/inventory/shopping-list/<id>/` | Détail liste | Admin |
| `/inventory/shopping-list/<id>/pdf/` | Export PDF | Admin |
| `/inventory/shopping-list/<id>/export-text/` | Export texte | Admin |
| `/inventory/api/toggle-purchased/<id>/` | Toggle acheté (AJAX) | Admin |

### Exemple de requête AJAX
```javascript
fetch('/inventory/api/toggle-purchased/123/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': '{{ csrf_token }}',
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => location.reload());
```

---

## 🎨 Templates

### Structure
```
templates/inventory/
├── dashboard.html           # Dashboard principal
├── inventory_list.html      # Liste articles
├── shopping_lists.html      # Grille listes
├── shopping_list_detail.html # Détail + édition
├── email_shopping_list.html # Email template HTML
└── email_shopping_list.txt  # Email template texte
```

### Couleurs & Styles
- 🔵 Bleu (#4F46E5) - Principale
- 🟢 Vert (#10B981) - Succès
- 🟡 Jaune (#F59E0B) - Alerte
- 🔴 Rouge (#EF4444) - Erreur/Critique

---

## 📧 Email

Peut partager une liste par email avec template HTML et texte:
```python
# À implémenter dans les vues
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Template: templates/inventory/email_shopping_list.html
# Contient tous les détails de la liste
```

---

## ⚙️ Signaux Django

### Auto-mises à jour
- `ShoppingListItem.save()` → Recalcule `total_cost` de la liste
- `ShoppingListItem.delete()` → Recalcule `total_cost` de la liste

### Logs
- Quand une liste est créée: log dans console

---

## 🐛 Tests Unitaires

```bash
python manage.py test inventory
```

Tests inclus:
- ✅ Création de catégories
- ✅ Auto-mise à jour du statut
- ✅ Création de listes
- ✅ Calcul des coûts
- ✅ Permissions admin
- ✅ Accès vues

---

## 📝 Notes Importantes

1. **Statut automatique**: Pas besoin de mettre à jour manuellement le statut, il se fait lors du `save()`

2. **Coût total**: Mis à jour automatiquement quand des articles sont ajoutés/supprimés

3. **Articles personnalisés**: Une liste peut avoir des articles non liés à l'inventaire via `custom_item_name`

4. **Permissions**: Toutes les vues vérifient `is_admin` (staff + not teacher)

5. **PDF Paysage**: Format A4 paysage pour meilleure lisibilité

---

## 🎓 Utilisation Recommandée

### Flux typique
1. 📦 **Admin crée les catégories et articles** → Dashboard
2. 🛒 **Planifier une liste** → Créer liste + ajouter articles
3. 📝 **Remplir les détails** → Quantités, prix, priorités
4. 📄 **Générer PDF** → Pour impression/envoi
5. ✅ **Marquer comme acheté** → En temps réel sur le site
6. 🔄 **Mises à jour stock** → Via admin Django

---

**Dernière mise à jour:** 2024
**Version:** 1.0
