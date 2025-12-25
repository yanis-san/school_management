# 🎯 QUICK START: Tableau de Bord Paiements

## 🚀 5 Secondes pour Commencer

### Étape 1: Accédez au dashboard
```
http://votre-site/finance/payments-dashboard/
```

### Étape 2: Choisissez vos filtres (optionnel)
```
Cohort: Choisissez un cours (ou laissez vide pour tous)
Modalité: En ligne? Présentiel? (ou les deux)
Type: Individuel? Groupe? (ou les deux)
```

### Étape 3: Cliquez "Filtrer"
```
Le tableau se met à jour instantanément
```

### Étape 4: Lisez le tableau
```
Cherchez les 🔴 IMPAYÉ pour voir qui doit payer
```

### Étape 5: Exportez en CSV (optionnel)
```
Cliquez "📥 CSV" pour télécharger
```

---

## 📊 Exemple Concret

### Vous êtes directeur(trice), vous voulez savoir:
### **"Qui n'a pas payé le Japonais en ligne cette année?"**

```
1. Allez à: /finance/payments-dashboard/
2. Cohort: Sélectionnez "Japonais N5"
3. Modalité: Sélectionnez "En ligne"
4. Cliquez "🔍 Filtrer"

RÉSULTAT: Tableau avec SEULEMENT Japonais en ligne
          Cherchez les lignes avec 🔴 IMPAYÉ
```

---

## 💡 10 Cas d'Usage Courants

### 1️⃣ Voir le total collecté ce mois-ci
```
→ Lire la boîte bleue "Total Payé"
```

### 2️⃣ Voir combien il nous reste à collecter
```
→ Lire la boîte rouge "Reste à Payer"
```

### 3️⃣ Quel est notre taux de recouvrement?
```
→ Lire la boîte violette "Pourcentage"
(ex: 75% = Bon)
```

### 4️⃣ Combien d'étudiants n'ont rien payé?
```
→ Regarder le compteur "🔴 Impayé"
(ex: 12 = 12 étudiants à relancer)
```

### 5️⃣ Qui paie ses dettes petit à petit?
```
→ Chercher les statuts "🟡 PARTIEL"
(ex: Alice doit 10,000 DA, a payé 6,000)
```

### 6️⃣ Analyser les paiements par modalité
```
Étape 1: Filtrer "En ligne" → Noter le %
Étape 2: Réinitialiser
Étape 3: Filtrer "Présentiel" → Comparer %
(ex: En ligne 80%, Présentiel 60% → En ligne paie mieux)
```

### 7️⃣ Comparer cours individuels vs groupe
```
Étape 1: Filtrer "Individuel" → Noter le %
Étape 2: Réinitialiser
Étape 3: Filtrer "Groupe" → Comparer %
```

### 8️⃣ Créer liste de rappels
```
Étape 1: Filtrer (ex: cohort)
Étape 2: Cliquez "📥 CSV"
Étape 3: Ouvrez dans Excel
Étape 4: Copier les noms des 🔴 IMPAYÉ
Étape 5: Créer courrier de rappel
```

### 9️⃣ Voir qui doit le plus
```
→ Regarder colonne "Reste"
→ Chercher les plus gros chiffres
(ex: "4000 DA" > "1000 DA")
```

### 🔟 Exclure les payés pour focus sur les impayés
```
Malheureusement: pas de filtre "Status"
MAIS: Tableau est trié (🔴 d'abord, puis 🟡, puis 🟢)
→ Regarder les premières lignes seulement
```

---

## 🎨 Comprendre les Couleurs

### Statuts (Colonnes "Statut")
```
🔴 IMPAYÉ  = ROUGE       → Urgence! Aucun paiement
🟡 PARTIEL = ORANGE      → Attention, paiement incomplet
🟢 PAYÉ    = VERT        → Tout bon, montant reçu
```

### Barre de Progression
```
████░░░░░ 40%  = Moins de moitié payé
████████░ 90%  = Presque tout payé
██████████100% = Entièrement payé
```

### Boîtes de Résumé
```
BLEU    = Total dû (tarif)
VERT    = Total collecté (payé)
ROUGE   = Pas encore reçu (reste)
VIOLET  = Pourcentage collecté
JAUNE   = Nombre d'élèves
```

---

## 🔒 Sécurité

**Qui peut accéder?**
```
✅ Admin du système
✅ Staff members
❌ Étudiants
❌ Utilisateurs non connectés
```

**Si vous n'avez pas accès:**
```
→ Contactez l'administrateur pour permissions
```

---

## 💾 Export CSV

### Format du fichier exporté:
```
Code | Étudiant | Cohort | Modalité | Tarif | Payé | Reste | % | Statut
2025-001 | Alice | Japonais | En ligne | 10000 | 6000 | 4000 | 60% | PARTIEL
2025-002 | Bob | Arabique | Présentiel | 8000 | 8000 | 0 | 100% | PAYÉ
...
```

### Comment utiliser:
```
1. Téléchargez le CSV
2. Ouvrez dans Excel/Calc
3. Triez, filtrez, créez des graphiques
4. Exportez vers Word pour courrier de rappel
```

---

## ⚡ Raccourcis Clavier

```
CTRL + Entrée  = Soumettre le formulaire de filtres
```

---

## 🐛 Problèmes Courants

### "Je ne vois aucun étudiant"
```
→ Assurez-vous que:
   1. Vous êtes connecté
   2. Il y a des inscriptions actives (is_active=True)
   3. Les cohorts existent
4. Les filtres ne bloquent pas tout (ex: modalité inexistante)
```

### "Les chiffres sont bizarres"
```
→ Cela signifie:
   - Un étudiant a payé plus que le tarif
   - Ou un paiement est enregistré pour un mauvais étudiant
   → Contactez l'admin pour vérifier les données
```

### "Je ne peux pas exporter"
```
→ Vérifiez:
   1. Votre navigateur permet les téléchargements
   2. Vous avez les permissions admin
   3. Essayez un autre navigateur
```

---

## 📚 Documentation Complète

**Pour plus de détails:**
```
→ Lire: GUIDE_TABLEAU_PAIEMENTS.md
→ Lire: IMPLEMENTATION_DASHBOARD_PAIEMENTS.md
```

---

## 🆘 Support

**Si vous avez un problème:**
```
1. Vérifiez que vous êtes admin
2. Essayez de réinitialiser les filtres
3. Rafraîchissez la page (F5)
4. Contactez le développeur avec screenshot
```

---

**Bon courage! 💪**

Le dashboard est maintenant prêt à vous aider à suivre les paiements! 💰
