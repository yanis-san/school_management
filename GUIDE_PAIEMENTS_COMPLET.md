# 📚 Guide Complet du Système de Paiement

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Les 3 entités principales](#les-3-entités-principales)
3. [Comment ça marche en pratique](#comment-ça-marche-en-pratique)
4. [Scénarios réels](#scénarios-réels)
5. [Ce que le système fait automatiquement](#ce-que-le-système-fait-automatiquement)
6. [Ce que vous devez faire manuellement](#ce-que-vous-devez-faire-manuellement)
7. [Guide pas à pas: ajouter une inscription](#guide-pas-à-pas-ajouter-une-inscription)
8. [Guide pas à pas: enregistrer un paiement](#guide-pas-à-pas-enregistrer-un-paiement)
9. [FAQ](#faq)
10. [Dépannage](#dépannage)

---

## Vue d'ensemble

Le système de paiement de l'école gère **les contrats entre étudiants et groupes de cours**, avec **suivi des tarifs** et **historique des paiements**.

### Concept clé
**Chaque inscription = une facture indépendante avec son propre solde**

```
Alice DURAND
├─ Inscription 1: Japonais Niveau 1 (5000 DA)
│  ├─ Payée: 3000 DA
│  └─ Reste: 2000 DA
│
└─ Inscription 2: Chinois Niveau 1 (4000 DA)
   ├─ Payée: 0 DA
   └─ Reste: 4000 DA
```

---

## Les 3 entités principales

### 1️⃣ **Tariff** = Le prix

**Définition**: Une liste de prix pré-définis que vous réutilisez.

**Caractéristiques**:
- ✅ Créé une fois et réutilisé pour plusieurs inscriptions
- ✅ Peut avoir un nom descriptif
- ✅ C'est juste un prix, rien de plus

**Exemples**:
```
- "Niveau 1 - 5000 DA"
- "Niveau 2 - 7000 DA"
- "Pack Privé - 3000 DA"
- "Tarif réduit - 3500 DA"
```

**Où créer?** Admin → Finance → Tariffs

---

### 2️⃣ **Enrollment** = Le contrat / L'inscription

**Définition**: Quand un étudiant s'inscrit à un groupe. C'est le **lien** entre l'étudiant et le groupe.

**Caractéristiques**:
- 🔗 Relie un étudiant à UN groupe
- 💰 Attribue UN tarif (prix) **unique à cette inscription**
- 📅 Enregistre la date d'inscription
- 📋 Définit le plan de paiement (totalité, mensuel, pack d'heures)
- ✅ Une inscription = une facture indépendante
- ⚠️ **IMPORTANT**: Plusieurs étudiants du même groupe peuvent avoir des tarifs DIFFÉRENTS

**Informations stockées**:
```
Enrollment {
  Étudiant: Alice DURAND
  Groupe: Japonais Niveau 1
  Tarif: 5000 DA          ← C'est le prix pour CETTE inscription (Alice)
  Remise: 0 DA
  Plan de paiement: Mensuel
  Date création: 2025-09-01
  Actif: Oui
}

Enrollment {
  Étudiant: Bob MARTIN
  Groupe: Japonais Niveau 1  ← Même groupe que Alice!
  Tarif: 4500 DA             ← Mais Bob paie moins (remise de -500 DA)
  Remise: 500 DA
  Plan de paiement: Totalité
  Date création: 2025-09-01
  Actif: Oui
}
```

**Important**: Chaque fois qu'Alice s'inscrit à un NEW groupe, vous créez une NOUVELLE Enrollment!
Et chaque Enrollment a **son propre tarif indépendant** - même si plusieurs étudiants sont dans le même groupe!

---

### 3️⃣ **Payment** = Le paiement

**Définition**: Chaque fois qu'Alice paie quelque chose, vous l'enregistrez.

**Caractéristiques**:
- ✅ Lié à UNE SEULE Enrollment (pas globale)
- ✅ Montant à votre choix
- ✅ Date de paiement
- ✅ Qui a enregistré (traçabilité)

**Exemple**:
```
Enrollment: Japonais 5000 DA
  ├─ Payment 1: +2000 DA (1er septembre)
  ├─ Payment 2: +2000 DA (5 octobre)
  └─ Payment 3: +1000 DA (3 novembre) = SOLDE

Reste = 5000 - (2000 + 2000 + 1000) = 0 DA ✅
```

---

## Comment ça marche en pratique

### Étape 1: Vous créez des Tariffs

**Quand?** Une seule fois au début, ou quand vous changez vos prix.

**Exemple de configuration minimale**:
```
Tariff 1:
  Nom: "Niveau 1 Standard"
  Prix: 5000 DA

Tariff 2:
  Nom: "Pack Privé"
  Prix: 3000 DA

Tariff 3:
  Nom: "Niveau 2 Avancé"
  Prix: 7000 DA
```

**Où?** Admin Dashboard → Finance → Tariffs → "Ajouter un tarif"

---

### Étape 2: Alice s'inscrit à Japonais

**Actions**:
1. Vous allez sur la page d'Alice (Étudiants → Alice DURAND)
2. Section "Inscriptions" → Cliquez sur "Ajouter une inscription"
3. Remplissez:
   - **Groupe**: Japonais Niveau 1 (sélectionner)
   - **Tarif**: "Niveau 1 Standard" (5000 DA) → sélectionner
   - **Plan de paiement**: "Totalité" ou "Mensuel"
   - Cliquez **Enregistrer**

**Résultat**:
```
✅ Enrollment créée
   Tarif: 5000 DA
   Payée: 0 DA
   Reste: 5000 DA
```

---

### Étape 3: Alice paie

**Première fois (septembre)**:
1. Alice vient payer 2000 DA
2. Vous allez sur la page d'Alice
3. Cliquez "+ Ajouter un paiement"
4. Remplissez:
   - **Enrollment**: Japonais (sélectionner)
   - **Montant**: 2000 DA
   - **Qui a enregistré**: Vous
   - Cliquez **Enregistrer**

**Résultat**:
```
✅ Payment enregistré
   Payée: 2000 DA
   Reste: 3000 DA
```

**Deuxième fois (octobre)**:
1. Alice paie 2000 DA
2. Même processus
3. Résultat: Reste: 1000 DA

**Troisième fois (novembre)**:
1. Alice paie 1000 DA
2. Résultat: Reste: 0 DA ✅ TERMINÉE

---

### Étape 4: Alice veut s'inscrire à Chinois (3 mois plus tard)

**Actions**:
1. Vous allez toujours sur la page d'Alice
2. Section "Inscriptions" → Cliquez sur "Ajouter une inscription" (ENCORE)
3. Remplissez:
   - **Groupe**: Chinois Niveau 1
   - **Tarif**: "Niveau 1 Standard" (5000 DA ou autre au choix)
   - **Plan de paiement**: Au choix
4. Cliquez **Enregistrer**

**Résultat**: Alice a MAINTENANT 2 Enrollments indépendantes!

```
Alice DURAND

Inscription 1: Japonais Niveau 1
├─ Tarif: 5000 DA
├─ Payée: 5000 DA (complètement payée ✅)
└─ Reste: 0 DA

Inscription 2: Chinois Niveau 1
├─ Tarif: 5000 DA
├─ Payée: 0 DA
└─ Reste: 5000 DA
```

---

## Scénarios réels

### Scénario 1: Alice paie la TOTALITÉ d'un coup

```
Septembre:
- Alice s'inscrit à Japonais: 5000 DA
- Alice paie immédiatement: 5000 DA
- Reste: 0 DA ✅ TERMINÉE

C'est fini pour Japonais!
```

---

### Scénario 2: Alice paie en 3 MENSUALITÉS

```
Septembre:
- Alice s'inscrit à Japonais: 5000 DA (plan: Mensuel)
- Alice paie: 2000 DA
- Reste: 3000 DA

Octobre:
- Alice paie: 2000 DA
- Reste: 1000 DA

Novembre:
- Alice paie: 1000 DA
- Reste: 0 DA ✅ TERMINÉE

Total payé: 5000 DA (2000 + 2000 + 1000)
```

**Note**: Le système NE divise PAS automatiquement 5000 DA en 3.
- Vous décidez à chaque fois: "Elle paie combien ce mois-ci?"
- C'est vous qui gérez les montants

---

### Scénario 3: Alice a PLUSIEURS inscriptions simultanées

```
Septembre:
├─ Inscription 1: Japonais 5000 DA
├─ Inscription 2: Anglais 4000 DA
└─ Frais annuels: 1000 DA
Total dû: 10 000 DA

Paiements:
- 15 sept: +2000 DA pour Japonais
- 20 sept: +2000 DA pour Anglais
- 25 sept: +1000 DA pour Frais annuels
- Paiements: 5000 DA
- Reste: 5000 DA

État actuel:
├─ Japonais: 5000 DA (payée complètement ✅)
├─ Anglais: 4000 DA (reste: 2000 DA)
└─ Frais: 1000 DA (payée complètement ✅)
```

---

## Ce que le système fait automatiquement

### ✅ Automatique

**1. Calcul du reste**
```
Reste = Tarif - (Somme de tous les paiements)
5000 - (2000 + 2000) = 1000 DA
```
Aucun calcul manuel nécessaire!

**2. Affichage du statut**
Le système affiche pour chaque inscription:
- Montant tarif
- Total payé
- Reste à payer
- Plan de paiement

**3. Historique des paiements**
Chaque paiement est enregistré avec:
- Date
- Montant
- Qui l'a enregistré
- Reste après ce paiement

**4. Page étudiant centralisée**
Vous voyez en un coup d'œil toutes les inscriptions d'Alice et leur statut financier.

---

## Ce que vous devez faire manuellement

### ⚠️ Manuel = Vous devez gérer

| Tâche | Détails |
|-------|---------|
| **Créer les Tariffs** | Une seule fois. Allez dans Admin → Finance → Tariffs |
| **Créer les Enrollments** | À chaque nouvelle inscription. Allez sur la page de l'étudiant → "Ajouter une inscription" |
| **Enregistrer les paiements** | À chaque fois qu'elle paie. Page étudiant → "+ Ajouter un paiement" |
| **Rappeler Alice si elle ne paie pas** | Le système ne vous envoie pas de rappels. À vous d'appeler! |
| **Diviser les montants pour mensuel** | Si elle paie par mensualité, le système ne divise PAS automatiquement. Vous décidez à chaque fois |
| **Gérer les remises** | Si vous donnez une remise (ex: -500 DA), vous le spécifiez dans l'Enrollment |
| **Marquer comme payée** | Les frais annuels: Admin → Étudiants → Sélectionner → "Marquer comme payé" |

---

## Guide pas à pas: ajouter une inscription

### Situation
Alice DURAND veut s'inscrire à Japonais Niveau 1 (tarif: 5000 DA).

### Étapes

#### 1️⃣ Ouvrir la page de l'étudiant
```
Accueil → Étudiants → Rechercher "Alice DURAND"
Cliquez sur Alice → Sa page s'ouvre
```

#### 2️⃣ Aller à la section Inscriptions
```
Sur sa page, cherchez la section "Inscriptions"
Bouton: "+ Ajouter une inscription"
```

#### 3️⃣ Remplir le formulaire d'inscription
```
Champ 1 - Groupe:
  ↓ Sélectionner "Japonais Niveau 1"

Champ 2 - Tarif:
  ↓ Sélectionner "Niveau 1 Standard" (5000 DA)
  
Champ 3 - Plan de paiement:
  ↓ Choisir:
    - "Totalité (Une fois)" = elle paie d'un coup
    - "Mensuel (Échéancier)" = elle paie en plusieurs fois
    - "Pack d'Heures" = système spécial pour heures achetées

Champ 4 - Remise (optionnel):
  ↓ Si elle a une remise (ex: -500 DA), sélectionner

Champ 5 - Heures (si Pack):
  ↓ Si plan "Pack d'Heures", entrer le nombre d'heures
```

#### 4️⃣ Valider
```
Cliquez "Enregistrer"
ou
"Créer l'Enrollment"
```

#### 5️⃣ Vérifier
```
Page d'Alice se rafraîchit
Vous voyez dans "Inscriptions":
  ✓ Japonais Niveau 1
  ✓ Tarif: 5000 DA
  ✓ Plan: Mensuel (ou autre)
  ✓ Payée: 0 DA
  ✓ Reste: 5000 DA
```

---

## Guide pas à pas: enregistrer un paiement

### Situation
Alice a payé 2000 DA pour son inscription à Japonais. Vous devez l'enregistrer.

### Étapes

#### 1️⃣ Ouvrir la page de l'étudiant
```
Accueil → Étudiants → Chercher "Alice DURAND"
Cliquez sur Alice
```

#### 2️⃣ Trouver l'inscription concernée
```
Section "Inscriptions"
Vous voyez:
  - Japonais Niveau 1 | 5000 DA | Payée: 0 DA | Reste: 5000 DA

Cliquez sur "Ajouter un paiement"
(ou "+ Ajouter un paiement")
```

#### 3️⃣ Remplir le formulaire de paiement
```
Champ 1 - Enrollment:
  ↓ La page pré-sélectionne "Japonais"
  ↓ Si Alice a plusieurs inscriptions, choisir la bonne

Champ 2 - Montant:
  ↓ Entrer: 2000

Champ 3 - Date (optionnel):
  ↓ Laisser "Aujourd'hui" ou entrer une date spécifique

Champ 4 - Enregistré par:
  ↓ Votre nom (pré-sélectionné)

Champ 5 - Note (optionnel):
  ↓ Ex: "Chèque reçu", "Espèces", "Virement CCP"
```

#### 4️⃣ Valider
```
Cliquez "Enregistrer payment"
ou
"Ajouter le paiement"
```

#### 5️⃣ Vérifier
```
La page se rafraîchit
Vous voyez:
  Historique des paiements:
  ├─ 15 oct, 14h30: +2000 DA (reste: 3000 DA)
  └─ Enregistré par: [Vous]
```

---

## FAQ

### Q1: Je dois créer un Tariff pour chaque groupe?
**R**: Non! 
- Si "Niveau 1" coûte toujours 5000 DA (peu importe la langue), créez UN SEUL Tariff "Niveau 1 - 5000 DA"
- Réutilisez ce même tarif pour toutes les inscriptions Niveau 1
- Créez un nouveau tarif seulement si le prix change (ex: "Niveau 2 - 7000 DA")

---

### Q2: Alice peut-elle avoir une remise?
**R**: Oui!
- Quand vous créez l'Enrollment, vous pouvez sélectionner une remise
- Exemple: Tarif 5000 DA - Remise 500 DA = Alice doit 4500 DA
- Vous devez créer les remises d'abord (Admin → Finance → Discounts)

---

### Q3: Que faire si Alice ne paie pas à temps?
**R**: Le système ne bloque rien:
- Le système enregistre juste "Reste: 3000 DA"
- À vous de rappeler Alice!
- Vous pouvez ajouter une note dans les paiements

---

### Q4: Et si Alice paie PLUS que le tarif?
**R**: 
- Resto = Tarif - Paiements
- Si elle paie 6000 DA pour un tarif de 5000 DA
- Resto = 5000 - 6000 = -1000 DA (surplus)
- C'est à votre discrétion: remboursement ou crédit pour prochaine inscription

---

### Q5: Peut-elle s'inscrire au même groupe deux fois?
**R**: Non, normalement le système ne le permet pas.
- Une Enrollment = un étudiant + un groupe unique
- Si elle veut continuer le même groupe, c'est une nouvelle année/session

---

### Q6: Les frais annuels (1000 DA) sont comptabilisés où?
**R**: C'est SÉPARÉ:
- Frais annuels: StudentAnnualFee (entité différente)
- Inscriptions: Enrollment
- Alice paie: Frais annuels (1000 DA) + Inscriptions (5000 DA + 4000 DA) = 10 000 DA total

---

### Q7: Comment voir le récapitulatif de ce que doit Alice?
**R**: Page étudiant:
1. Allez sur Alice
2. Vous voyez:
   - **Inscriptions actives**: List avec Reste pour chaque
   - **Historique des paiements**: Tous les paiements
   - **Frais annuels**: Payés ou non payés
   - **Total dû**: Somme de tous les restes

---

### Q8: Je peux modifier une Enrollment après sa création?
**R**: Oui, partiellement:
- ✅ Modifier le plan de paiement
- ✅ Ajouter/modifier une remise
- ✅ Désactiver (marquer comme non-actif)
- ❌ Changer le tarif (cela impacterait le calcul)

**Mieux**: Créer une nouvelle Enrollment si vous devez changer le tarif.

---

### Q9: Où voir les paiements non-associés ou erreurs?
**R**: Admin → Finance → Payments
- Liste de TOUS les paiements
- Vous pouvez filtrer par étudiant, date, montant
- Vous pouvez modifier/supprimer si erreur

---

### Q10: Comment exporter/imprimer les factures?
**R**: Via les Rapports:
- Rapports → Étudiants → Tous les étudiants
- Rapports → Annuels → Par année
- Les PDFs affichent: Nom, Inscriptions, Tarif, Payé, Reste

---

### Q11: Plusieurs étudiants dans le MÊME groupe peuvent-ils avoir des tarifs DIFFÉRENTS?
**R**: **OUI! C'est normal et bien géré.**

**Exemple**:
```
Groupe: Japonais Niveau 1

Alice DURAND
├─ Enrollment 1: Japonais (Tarif: 5000 DA, Remise: 0)
│  └─ Doit: 5000 DA

Bob MARTIN
├─ Enrollment 2: Japonais (Tarif: 5000 DA, Remise: -500 DA)
│  └─ Doit: 4500 DA (car inscription avec remise)

Charlie DUPONT
├─ Enrollment 3: Japonais (Tarif: 5000 DA, Remise: -1000 DA)
│  └─ Doit: 4000 DA (prix réduit pour étudiant fidèle)
```

**Pourquoi ça fonctionne?**
- Chaque Enrollment est **indépendante**
- Chaque Enrollment a son propre tarif + remise
- Les calculs restent corrects: `Reste = Tarif - Paiements`

**Exemple de paiements:**
```
Alice:
  Inscription: 5000 DA
  Paiement 1: +2000 DA (sept)
  Paiement 2: +3000 DA (oct)
  Reste: 0 DA ✅

Bob:
  Inscription: 5000 DA - 500 DA (remise) = 4500 DA
  Paiement 1: +2000 DA (sept)
  Paiement 2: +2000 DA (oct)
  Paiement 3: +500 DA (nov)
  Reste: 0 DA ✅

Charlie:
  Inscription: 5000 DA - 1000 DA (remise) = 4000 DA
  Paiement 1: +4000 DA (sept)
  Reste: 0 DA ✅
```

**Résultat dans le groupe:**
- Groupe Japonais Niveau 1: 3 étudiants
- Revenus totaux: 5000 (Alice) + 4500 (Bob) + 4000 (Charlie) = 13 500 DA
- Chacun suit indépendamment son solde ✅

**Donc oui, le système gère parfaitement ce cas!**

---

## Dépannage

### Problème: Alice a 2 Enrollments pour le MÊME groupe!
**Cause**: Vous avez créé 2 fois accidentellement.
**Solution**:
1. Admin → Students → Enrollments
2. Chercher les 2 doublons
3. Cliquer sur le doublon → Bouton "Supprimer"
4. Refaire une seule Enrollment

---

### Problème: Un paiement a été enregistré sur le mauvais groupe
**Cause**: Vous avez sélectionné la mauvaise Enrollment.
**Solution**:
1. Admin → Finance → Payments
2. Trouver le paiement erroné
3. Cliquer dessus → Modifier
4. Changer l'Enrollment vers la bonne
5. Cliquez "Enregistrer"

---

### Problème: Le reste affiche un nombre bizarre
**Cause**: Peut-être un paiement erreur ou tarif mal enregistré.
**Solution**:
1. Vérifier: Tarif = ?? DA
2. Vérifier: Paiements = ?? + ?? = ??
3. Calculer manuellement: Tarif - Total Paiements
4. Si différent du système, contacter admin/dev

---

### Problème: Je ne vois pas le bouton "Ajouter une inscription"
**Cause**: Peut-être les permissions.
**Solution**:
1. Vérifier que vous êtes connecté comme Admin
2. Vérifier que vous êtes sur la bonne page étudiant
3. Recharger la page (F5)

---

### Problème: Le Tariff que je veux utiliser n'existe pas
**Cause**: Il n'a pas été créé.
**Solution**:
1. Admin Dashboard → Finance → Tariffs
2. Cliquez "+ Ajouter un tarif"
3. Remplissez: Nom + Montant
4. Cliquez "Enregistrer"
5. Retournez créer l'Enrollment

---

## Résumé / Checklist

### Avant chaque inscription, vérifiez:
- [ ] L'étudiant existe dans le système
- [ ] Le groupe existe et est actif
- [ ] Le Tariff pour ce groupe existe
- [ ] Vous savez quel plan de paiement Alice choisit

### À chaque paiement:
- [ ] Vous avez le montant exact
- [ ] Vous sélectionnez la bonne Enrollment
- [ ] Vous enregistrez la date correcte
- [ ] Vous vérifiez que le reste est correct après

### À chaque fin de paiement:
- [ ] Reste = 0 DA ✅ Inscription payée
- [ ] Vous pouvez marquer l'Enrollment comme complète (si système le permet)
- [ ] Vous gardez une trace (ex: "Payée intégralement en nov")

---

## Terminologie rapide

| Terme | Signification |
|-------|--------------|
| **Enrollment** | Inscription, contrat entre étudiant et groupe |
| **Tariff** | Prix unitaire appliqué à une inscription |
| **Payment** | Un paiement (une entrée d'argent) |
| **Balance Due** | Reste à payer |
| **Discount** | Remise appliquée |
| **Plan de paiement** | Totalité, Mensuel, ou Pack d'heures |
| **Actif** | Oui = l'inscription est en cours |
| **Frais annuels** | StudentAnnualFee, 1000 DA par année |

---

**Dernière mise à jour**: 18 décembre 2025
