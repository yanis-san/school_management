# GUIDE: Tableau de Bord Paiements Étudiants

## 📊 Vue d'ensemble

Le **Tableau de Bord Paiements** vous offre une vue synthétique complète de tous les paiements des étudiants avec la possibilité de filtrer et analyser les données en temps réel.

**URL d'accès:** `http://votre-site/finance/payments-dashboard/`

---

## 🎯 Fonction Principale

**Répondre à la question:** *Qui a payé, qui n'a pas payé, et combien reste-t-il à chacun?*

Avec la capacité de filtrer par:
- ✅ **Cohort** - Voir les paiements d'une classe spécifique
- ✅ **Modalité** - ONLINE (📱 En ligne) ou IN_PERSON (🏫 Présentiel)
- ✅ **Type** - Individuel (👤) ou Groupe (👥)

---

## 🔍 Filtres Disponibles

### 1. Cohort
Sélectionnez un cohort spécifique pour voir **uniquement les paiements de cet enseignement**.

```
Exemple: Filtrer "Japonais N5" → Affiche SEULEMENT les étudiants de Japonais
```

### 2. Modalité
Filtrez par mode d'enseignement:
- **📱 En ligne** (ONLINE)
- **🏫 Présentiel** (IN_PERSON)

```
Exemple: "En ligne" → Montre les paiements pour les cours en ligne uniquement
```

### 3. Type
Distinguez les cours individuels des cours de groupe:
- **👤 Individuel** - Cours particuliers
- **👥 Groupe** - Classes groupées

```
Exemple: "Individuel" → Affiche SEULEMENT les paiements des cours particuliers
```

---

## 📈 Statistiques Principales

### Première Ligne: Résumé Financier

| Stat | Signification |
|------|---------------|
| **Total Tarif** | Montant total que tous les étudiants DOIVENT payer |
| **Total Payé** | Montant total déjà collecté |
| **Reste à Payer** | Différence entre tarif et paiements |
| **Pourcentage** | Taux de recouvrement (%) |
| **Inscriptions** | Nombre total d'élèves filtrés |

### Deuxième Ligne: Compteurs par Statut

```
🔴 IMPAYÉ    - Étudiants qui n'ont rien payé
🟡 PARTIEL   - Étudiants qui ont payé partiellement
🟢 PAYÉ      - Étudiants qui ont tout payé
```

---

## 📋 Tableau de Détail

### Colonnes du Tableau

| Colonne | Description | Exemple |
|---------|-------------|---------|
| **Étudiant** | Nom de l'étudiant + Code étudiant | Alice (2025-001) |
| **Cohort** | Nom du cours/cohort | Japonais N5 |
| **Modalité** | En ligne ou Présentiel + Individuel/Groupe | 📱 En ligne, 👤 Indiv. |
| **Tarif** | Montant que l'étudiant doit payer | 10,000 DA |
| **Payé** | Montant déjà collecté | 6,000 DA |
| **Reste** | Montant encore dû | 4,000 DA |
| **Avancement** | Barre visuelle + pourcentage | ████░░░░ 60% |
| **Statut** | Résumé du paiement | 🟡 PARTIEL |

---

## 💡 Cas d'Usage

### Cas 1: Voir qui n'a pas payé en ligne

```
1. Modalité: "En ligne"
2. Cliquer sur "🔍 Filtrer"
3. Chercher les lignes avec statut "🔴 IMPAYÉ"
```

**Résultat:** Tous les étudiants en ligne qui n'ont rien payé

---

### Cas 2: Suivi des paiements pour Arabique

```
1. Cohort: Sélectionner "Arabique DELF"
2. Cliquer "🔍 Filtrer"
```

**Résultat:** Tableau avec SEULEMENT les paiements pour Arabique

---

### Cas 3: Analyser les cours individuels

```
1. Type: "Individuel"
2. Cliquer "🔍 Filtrer"
```

**Résultat:** Tableau avec SEULEMENT les cours particuliers

---

### Cas 4: Combiner plusieurs filtres

```
1. Cohort: "Chinois B1"
2. Modalité: "Présentiel"
3. Type: "Groupe"
4. Cliquer "🔍 Filtrer"
```

**Résultat:** Étudiants de Chinois B1 en présentiel, cours de groupe

---

## 📥 Export en CSV

Cliquez sur le bouton **"📥 CSV"** pour télécharger les données actuelles dans un fichier Excel.

```
Fichier généré: paiements.csv

Contenu:
- Code étudiant
- Nom
- Cohort
- Modalité
- Tarif
- Montant payé
- Reste à payer
- Pourcentage
- Statut
```

**Utilité:** Analyser les données dans Excel, créer des rapports personnalisés, faire de statistiques avancées.

---

## 🎨 Codes Couleur

### Statuts de Paiement

```
🔴 IMPAYÉ   = Rouge       → Aucun paiement reçu
🟡 PARTIEL  = Jaune       → Paiement reçu mais incomplet
🟢 PAYÉ     = Vert        → Montant intégral reçu
```

### Barre de Progression

La barre visuelle montre le pourcentage du tarif payé:
- **Vide (blanc)** = 0% payé
- **Remplie (bleue)** = Progressif selon le pourcentage
- **Complètement remplie** = 100% payé (🟢 PAYÉ)

---

## 🔧 Utilisation Avancée

### Analyse par Modalité

**Question:** Quel est le taux de recouvrement pour l'en ligne vs présentiel?

```
Étape 1: Filtrer par "En ligne" → Noter le pourcentage
Étape 2: Réinitialiser les filtres
Étape 3: Filtrer par "Présentiel" → Comparer les pourcentages
```

---

### Identifier les Gros Impayés

**Question:** Quels sont les étudiants qui doivent le plus d'argent?

```
Regarder la colonne "Reste" en haut du tableau
Trier mentalement par montant décroissant
Chercher les "🔴 IMPAYÉ" avec les plus gros tarifs
```

---

### Comparaison Individuel vs Groupe

```
Étape 1: Filtrer Type = "Individuel" → Noter le total payé
Étape 2: Filtrer Type = "Groupe" → Comparer le total payé
Étape 3: Analyser les taux de recouvrement respectifs
```

---

## ⚙️ Configuration des Filtres

Tous les filtres se combinent (ET logique):

```
Si vous sélectionnez:
- Cohort: "Japonais"
- Modalité: "En ligne"

Vous verrez: Les paiements des étudiants de Japonais qui sont en ligne
(exclut les étudiants de Japonais en présentiel)
```

---

## 📊 Interprétation des Données

### Scénario 1: Forte Collecte
```
Total Payé: 500,000 DA
Total Tarif: 600,000 DA
Pourcentage: 83%

→ Bon taux de recouvrement (83%)
→ SEULEMENT 17% à relancer
```

### Scénario 2: Faible Collecte
```
Total Payé: 100,000 DA
Total Tarif: 500,000 DA
Pourcentage: 20%

→ Taux de recouvrement très faible (20%)
→ 80% à relancer urgemment!
```

---

## 🚀 Prochaines Actions

Après utiliser le dashboard:

1. **Identifier les 🔴 IMPAYÉ** → Liste des étudiants à relancer
2. **Exporter en CSV** → Préparer des rappels/courriers
3. **Analyser par Cohort** → Voir quel cours a les meilleurs taux de paiement
4. **Filtrer par Modalité** → Comparer performance en ligne vs présentiel

---

## 📞 Support

Si vous avez des questions sur:
- **Les filtres:** Vérifiez la section "Filtres Disponibles"
- **L'interprétation:** Consultez "Interprétation des Données"
- **L'export CSV:** Lire la section "Export en CSV"

---

**Dernière mise à jour:** Décembre 2025
**Version:** 1.0
**Statut:** Production ✅
