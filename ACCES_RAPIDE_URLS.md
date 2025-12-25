# 🔗 ACCÈS RAPIDE - URLs Directes

## 📱 Dashboard Principal

### URL de base
```
http://localhost:8000/finance/payments-dashboard/
```

**Production:** Remplacez `localhost:8000` par votre domaine

---

## 🎯 Exemples d'URLs Prêtes à Utiliser

### 1. Voir TOUS les paiements
```
http://localhost:8000/finance/payments-dashboard/
```

### 2. Voir les paiements du Japonais
```
http://localhost:8000/finance/payments-dashboard/?cohort=1
```
⚠️ Remplacez `1` par l'ID réel du cohort Japonais

### 3. Voir les paiements EN LIGNE
```
http://localhost:8000/finance/payments-dashboard/?modality=ONLINE
```

### 4. Voir les paiements EN PRÉSENTIEL
```
http://localhost:8000/finance/payments-dashboard/?modality=IN_PERSON
```

### 5. Voir UNIQUEMENT les cours individuels
```
http://localhost:8000/finance/payments-dashboard/?individual=1
```

### 6. Voir UNIQUEMENT les cours de groupe
```
http://localhost:8000/finance/payments-dashboard/?individual=0
```

### 7. Combiner: Japonais + En ligne
```
http://localhost:8000/finance/payments-dashboard/?cohort=1&modality=ONLINE
```

### 8. Combiner: Arabique + Présentiel + Groupe
```
http://localhost:8000/finance/payments-dashboard/?cohort=2&modality=IN_PERSON&individual=0
```

### 9. EXPORTER tous les paiements EN CSV
```
http://localhost:8000/finance/payments-dashboard/?export=csv
```

### 10. EXPORTER paiements Japonais EN CSV
```
http://localhost:8000/finance/payments-dashboard/?cohort=1&export=csv
```

---

## 🔍 Comment Trouver les IDs des Cohorts

### Option 1: Via l'admin Django
```
1. Allez à http://localhost:8000/admin/academics/cohort/
2. Cliquez sur un cohort (ex: "Japonais")
3. L'URL affiche: /admin/academics/cohort/1/
4. Le "1" est l'ID → Utilisez dans ?cohort=1
```

### Option 2: Faire un test
```
1. Allez à /finance/payments-dashboard/
2. Utilisez le dropdown "Cohort"
3. Faites F12 (inspect)
4. Recherchez le cohort → Notez la valeur
```

### Exemple d'URL complète avec IDs
```
// Supposons:
// - Japonais = ID 5
// - Arabique = ID 7
// - Chinois = ID 9

http://localhost:8000/finance/payments-dashboard/?cohort=5&modality=ONLINE&export=csv
```

---

## 📋 Paramètres Disponibles

| Paramètre | Valeurs | Exemple |
|-----------|---------|---------|
| `cohort` | ID du cohort (chiffre) | `?cohort=1` |
| `modality` | `ONLINE` ou `IN_PERSON` | `?modality=ONLINE` |
| `individual` | `1` (oui) ou `0` (non) | `?individual=1` |
| `export` | `csv` | `?export=csv` |

---

## 🔗 URLs Complètes Testées

### Scénario 1: Directeur veut voir les impayés du Japonais
```
http://localhost:8000/finance/payments-dashboard/?cohort=5

Résultat: Tableau avec SEULEMENT Japonais
Action: Chercher les 🔴 IMPAYÉ
```

### Scénario 2: Analyste veut exporter tout en ligne
```
http://localhost:8000/finance/payments-dashboard/?modality=ONLINE&export=csv

Résultat: CSV téléchargé avec tous les cours en ligne
```

### Scénario 3: Directeur compare individuel vs groupe
```
Étape 1: http://localhost:8000/finance/payments-dashboard/?individual=1
         → Noter pourcentage
Étape 2: http://localhost:8000/finance/payments-dashboard/?individual=0
         → Comparer pourcentage
```

---

## 🎓 Cas Réels

### "Je suis directeur du Japonais, je veux juste mes paiements"
```
Allez directement à:
http://localhost:8000/finance/payments-dashboard/?cohort=5

Remplacez 5 par l'ID de Japonais
```

### "Je veux exporter tous nos impayés pour envoyer des courriers"
```
URL base:
http://localhost:8000/finance/payments-dashboard/?modality=ONLINE&export=csv

Puis dans Excel:
- Filtrez Status = "IMPAYÉ"
- Copiez les noms
- Créez les lettres
```

### "Je veux analyser: en ligne paie-t-il mieux?"
```
Comparez ces deux URLs:

EN LIGNE:
http://localhost:8000/finance/payments-dashboard/?modality=ONLINE
→ Lire "Pourcentage"

PRÉSENTIEL:
http://localhost:8000/finance/payments-dashboard/?modality=IN_PERSON
→ Lire "Pourcentage"

→ Comparer les %
```

---

## 🔐 Sécurité

```
⚠️  Vous DEVEZ être connecté comme admin
⚠️  Les URLs sont directes (pas de token sécurisé)
✅  Utilisez en production uniquement sur HTTPS
✅  Les utilisateurs normaux ne peuvent pas accéder
```

---

## 🧪 Tester Localement

### Démarrer le serveur
```powershell
.venv\Scripts\Activate.ps1
python manage.py runserver
```

### Test 1: Accès sans filtre
```
http://localhost:8000/finance/payments-dashboard/
```
✅ Devrait afficher TOUS les étudiants avec paiements

### Test 2: Filtre cohort
```
http://localhost:8000/finance/payments-dashboard/?cohort=1
```
✅ Devrait afficher SEULEMENT le cohort ID=1

### Test 3: Export CSV
```
http://localhost:8000/finance/payments-dashboard/?export=csv
```
✅ Devrait télécharger un fichier `paiements.csv`

### Test 4: Combiné
```
http://localhost:8000/finance/payments-dashboard/?cohort=1&modality=ONLINE&individual=1&export=csv
```
✅ Devrait télécharger un CSV avec:
- Cohort ID=1
- Modalité: En ligne
- Type: Individuel

---

## 📝 Copier/Coller Rapide

### Copier la base (localement)
```
http://localhost:8000/finance/payments-dashboard/
```

### Copier la base (production)
```
https://votresite.com/finance/payments-dashboard/
```

### Puis ajouter vos paramètres
```
?cohort=1&modality=ONLINE&individual=1&export=csv
```

---

## 🚀 Bookmarks Suggérés

**Sauvegardez ces URLs dans vos favoris:**

```
📌 Tous les paiements
http://localhost:8000/finance/payments-dashboard/

📌 Paiements Japonais
http://localhost:8000/finance/payments-dashboard/?cohort=5

📌 Paiements en ligne
http://localhost:8000/finance/payments-dashboard/?modality=ONLINE

📌 Export tous les impayés
http://localhost:8000/finance/payments-dashboard/?export=csv
```

---

## 🆘 Erreurs Courants

### "Page not found (404)"
```
✅ Solution: Vérifiez que Django tourne
             Remplacez localhost par le bon domaine
```

### "Redirect to login"
```
✅ Solution: Connectez-vous d'abord
             Vous DEVEZ avoir les droits admin
```

### "Tableau vide"
```
✅ Solution: Vérifiez que:
             1. Il y a des cohorts créés
             2. Il y a des enrollments actifs
             3. Les filtres ne bloquer pas tout
```

---

**Prêt à utiliser! 🚀**

Marquez cette page en favori pour accès rapide! ⭐
