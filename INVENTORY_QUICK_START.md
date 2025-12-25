# 🎯 GUIDE D'ACCÈS RAPIDE - INVENTAIRE

## 🚀 Démarrage Rapide

### 1. **Connectez-vous**
   - URL: `/login/`
   - Utilisateur: Admin uniquement
   - Accès: Professeurs bloqués ❌

### 2. **Accédez au Dashboard Inventaire**
   - URL: `/inventory/`
   - Vous verrez: Stats, articles critiques, listes récentes

### 3. **Pages Principales**
   - **Dashboard**: `/inventory/`
   - **Articles**: `/inventory/items/`
   - **Listes**: `/inventory/shopping-lists/`

---

## 📊 DASHBOARD (`/inventory/`)

**Affiche:**
- 📦 Total articles en inventaire
- ✅ Articles en stock normal
- ⚠️ Articles en stock faible (alerte)
- ❌ Articles en rupture
- 🚨 Articles critiques (obligatoires + problématiques)
- 🛒 Listes d'achat récentes

**Actions disponibles:**
- Voir tous les articles
- Gérer listes d'achat
- Ajouter un nouvel article

---

## 📋 ARTICLES (`/inventory/items/`)

**Filtrer par:**
- 🔍 Recherche par nom/description
- 📂 Catégorie
- 📊 Statut (OK/Faible/Rupture)
- 🔴 Articles obligatoires uniquement

**Voir:**
- Nom et catégorie
- Quantité actuelle vs minimum
- Unité
- Statut (code couleur)
- Flag article obligatoire

**Actions:**
- ✎ Éditer via Admin
- ➕ Ajouter nouveau

---

## 🛒 LISTES D'ACHAT (`/inventory/shopping-lists/`)

**Format:** Grille de cartes

**Chaque carte affiche:**
- Titre de la liste
- 📅 Date d'événement
- 📝 Nombre d'articles
- 💰 Coût total
- 📊 Statut (Brouillon/En cours/Complété)

**Actions par liste:**
- 👁️ Voir détails
- 📄 Télécharger PDF
- ✎ Éditer

---

## 📝 DÉTAIL LISTE (`/inventory/shopping-list/<id>/`)

**Section Info:**
- Créée par (utilisateur)
- Date d'événement
- Description
- Statut
- Coût total

**Section Progression:**
- Barre % d'achats complétés
- X/Y articles achetés

**Tableau Articles:**
| # | Article | Qté | Unité | Prix U. | Total | État | Priorité |
|---|---------|-----|-------|---------|-------|------|----------|

**Actions par article:**
- ☑️ Cocher comme acheté (AJAX)
- ✎ Modifier
- Voir date d'achat

**Actions globales:**
- 📄 Télécharger PDF
- 📧 Exporter texte

---

## 🔥 STATUTS & CODES COULEUR

### Statut Article
| Statut | Couleur | Icon | Signification |
|--------|--------|------|---------------|
| ✅ Stock OK | Vert | ✅ | Quantité > minimum |
| ⚠️ Stock Faible | Jaune | ⚠️ | Quantité = minimum |
| ❌ Rupture | Rouge | ❌ | Quantité = 0 |
| 📦 En commande | Gris | 📦 | Ordre en attente |

### Statut Liste
| Statut | Couleur | Icon | Signification |
|--------|--------|------|---------------|
| 📝 Brouillon | Gris | 📝 | En création |
| 🔄 En cours | Bleu | 🔄 | Achats commencés |
| ✅ Complété | Vert | ✅ | Tous achetés |

---

## 💡 ASTUCES D'UTILISATION

### 1. **Créer une liste rapidement**
   1. Aller à `/inventory/shopping-lists/`
   2. Cliquer "➕ Nouvelle liste"
   3. Remplir: titre, date, description
   4. Sauvegarder
   5. Admin: ajouter articles

### 2. **Marquer des achats**
   - Sur page détail liste
   - Cocher la case pour chaque article
   - La case se coche en AJAX
   - Progression % se met à jour automatiquement

### 3. **Imprimer une liste**
   1. Ouvrir détail liste
   2. Cliquer "📄 Télécharger PDF"
   3. Fichier téléchargé
   4. Imprimer directement

### 4. **Copier une liste**
   1. Ouvrir détail liste
   2. Cliquer "📋 Exporter texte"
   3. Copier le texte
   4. Coller où besoin

### 5. **Filtrer articles**
   - Recherche: tape le nom
   - Catégorie: sélectionne dans dropdown
   - Statut: choisir OK/Faible/Rupture
   - Obligatoires: cocher pour voir seulement

---

## ⚙️ ADMIN DJANGO

### Accéder à Admin
- URL: `/admin/`
- Aller à "Inventaire"

### Sections Admin
- **ItemCategory** - Catégories
- **InventoryItem** - Articles
- **ShoppingList** - Listes d'achat
- **ShoppingListItem** - Éléments listes

### Avantages Admin
- CRUD complet
- Édition inline
- Filtres avancés
- Changements en masse

---

## 🔢 DONNÉES DE TEST

### Déjà existantes
```
5 Catégories:
  - Fournitures scolaires
  - Nettoyage
  - Fournitures de bureau
  - Matériel pédagogique
  - Produits hygiéniques

10 Articles:
  - Cahiers A4, Stylos bleus, Gommes
  - Produit nettoyant, Papier toilette
  - Classeurs, Agrafes
  - Tableaux blancs, Marqueurs
  - Savon liquide

2 Listes:
  - Achat rentrée scolaire (draft)
  - Fournitures nettoyage (en cours)
```

### Régénérer données
```bash
python manage.py seed_inventory
```

---

## 📊 RAPPORTS POSSIBLES

### Depuis le Dashboard
- Nombre total d'articles
- Articles critiques à commander
- Stock à reconstituer

### Depuis les Listes
- Coût par événement
- Articles les plus achetés
- Progression d'achat

### Export
- PDF pour imprimer
- Texte pour archiver

---

## 🔐 PERMISSIONS

### Qui peut voir?
- ✅ Admin (staff + not teacher)
- ❌ Professeurs (no access)
- ❌ Non connecté (redirige login)

### Chaque page demande permission

---

## 🛠️ MAINTENANCE

### Sauvegarder données
- Django backup DB
- Export admin CSV

### Archiver listes
- Marquer comme "complété"
- Garder historique

### Ajouter articles
- Via admin + formulaire
- Importe catégories

---

## 📞 SUPPORT

### Si problème:
1. Vérifier connecté en tant qu'admin
2. Vérifier JavaScript activé (AJAX)
3. Vérifier navigateur recent
4. Vérifier permissions

### Logs debug
- Console Django: `python manage.py shell`
- Admin logs: `/admin/admin/logentry/`

---

## 🎯 WORKFLOW STANDARD

```
1. PLANIFIER
   └─ Créer liste d'achat
      └─ Ajouter articles

2. ORGANISER
   └─ Définir priorités
   └─ Ajouter prix/fournisseur
   └─ Valider dates

3. EXÉCUTER
   └─ Imprimer ou accéder en ligne
   └─ Cocher achats
   └─ Mises à jour prix

4. ARCHIVER
   └─ Marquer comme complété
   └─ Garder pour historique
```

---

## 📱 ACCÈS MOBILE

**Responsive Design:**
- ✅ Fonctionne sur téléphone
- ✅ Fonctionne sur tablette
- ✅ Fonctionne sur desktop

**Optimisé pour:**
- Android + iOS
- Chrome, Firefox, Safari
- Écrans 320px - 1920px

---

**Dernière mise à jour:** 2024
**Version:** 1.0
