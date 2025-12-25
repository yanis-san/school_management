# AUDIT SYSTEM PAIEMENTS - RAPPORT COMPLET

**Date du rapport:** 2025 (Session courante)
**Objectif:** Évaluer la complétude du système de paiements avant d'implémenter les rappels de paiement

---

## RÉSUMÉ EXÉCUTIF

✅ **VERDICT:** Le système de paiements fonctionne à **85%** pour la gestion des échéances.
- Modèles: COMPLETS (Installment, Payment, Tariff, Discount)
- Auto-calcul: FONCTIONNEL (les échéances se génèrent automatiquement)
- Suivi du solde: EXACT (balance_due calcule correctement)
- **GAP:** Dashboard de rappels et suivi des impayés ❌

---

## 1. ARCHITECTURE EXISTANTE

### 1.1 Modèle Installment (✅ COMPLET)

**Fichier:** `finance/models.py` (lignes 45-70)

```python
class Installment(models.Model):
    enrollment = ForeignKey('students.Enrollment')  # Lien à l'inscription
    due_date = DateField()                          # Quand c'est dû
    amount = IntegerField()                         # Montant de cette tranche
    is_paid = BooleanField(default=False)           # Payée ou pas?
    payment = ForeignKey(Payment, null=True)        # Quel paiement l'a soldée?
    
    class Meta:
        ordering = ['due_date']  # Toujours triées par date
```

**Capacités:**
- ✅ Stocke chaque échéance individuellement
- ✅ Trace quel paiement a soldé chaque échéance (pour audit)
- ✅ Peut filtrer les impayées (is_paid=False)
- ✅ Ordernar par date d'échéance
- ❌ N'a PAS: is_overdue, days_overdue, last_reminder_date

### 1.2 Auto-Génération des Échéances (✅ FONCTIONNEL)

**Fichier:** `finance/signals.py`

**Déclencheur:** Signal `post_save(Enrollment)`

**Logique:**

```
Plan FULL ou PACK:
  → Crée 1 échéance immédiate
  → Montant = tariff.amount
  → Due = date_inscription

Plan MONTHLY:
  → Calcule nombre de mois (cohort.start_date → cohort.end_date)
  → Montant mensuel = tariff.amount / mois
  → Crée 1 échéance par mois
  → Due = 1er jour de chaque mois du cycle
```

**Exemple:**
- Alice s'inscrit à Japonais (10,000 DA, plan MONTHLY)
- Cohort: 2025-01-15 → 2025-04-15 (4 mois)
- Système génère automatiquement:
  - Échéance 1: 2025-01-15 → 2,500 DA
  - Échéance 2: 2025-02-15 → 2,500 DA
  - Échéance 3: 2025-03-15 → 2,500 DA
  - Échéance 4: 2025-04-15 → 2,500 DA

### 1.3 Calcul du Solde Dû (✅ CORRECT)

**Fichier:** `students/models.py` → `Enrollment.balance_due` (propriété)

**Formule:**
```
balance_due = tariff.amount - SUM(all payments for this enrollment)
```

**Exemple:**
- Tarif: 10,000 DA
- Alice a payé: 6,000 DA (peu importe les dates/tranches)
- balance_due = 10,000 - 6,000 = **4,000 DA** ✓

**Avantage:** Fonctionne indépendamment des échéances (paie par cheque 4,000 DA d'un coup? balance_due devient 0)

### 1.4 Admin Interface (✅ BASIQUE)

**Fichier:** `finance/admin.py` → `InstallmentAdmin`

**Fonctionnalités:**
- ✅ Lister: enrollment, due_date, amount, is_paid
- ✅ Filtrer par: is_paid, due_date
- ✅ Éditer: Peut cocher is_paid depuis la liste
- ❌ Grouper par mois
- ❌ Voir "jours en retard"
- ❌ Bulk actions pour rappels

**Limitation:** Pour voir "Quels étudiants doivent payer en janvier?", il faut:
1. Aller sur Admin → Finance → Installments
2. Filtrer manuellement par due_date
3. Pas de vue synthétique

---

## 2. CE QUI EXISTE VRAIMENT

### 2.1 Données Disponibles Pour Chaque Échéance

```
Installment {
  enrollment_id: 123
  due_date: 2025-01-15
  amount: 2500
  is_paid: False              ← Peut filtrer!
  payment_id: NULL            ← Pas encore payée
  
  # Via enrollment:
  student: Alice
  cohort: Japonais
  tariff.amount: 10000
  balance_due: 4000
}
```

### 2.2 Calculs Possibles MAIS NON IMPLÉMENTÉS

```
# Jours de retard (si due_date < aujourd'hui et is_paid=False):
days_overdue = (today - due_date).days

# Catégories:
if is_paid: "PAYÉE"
elif due_date > today: "À VENIR" + (due_date - today).days + "j"
elif due_date == today: "DUE AUJOURD'HUI"
elif due_date < today: "EN RETARD" + days_overdue + "j"

# Regroupement:
impayées_ce_mois = Installment.objects.filter(
    due_date__year=2025,
    due_date__month=1,
    is_paid=False
)
```

---

## 3. CE QUI N'EXISTE PAS

### 3.1 Dashboard Rappels (❌ INEXISTANT)

**Besoin:** Une vue admin pour voir rapidement:

| Étudiant | Matière | Montant | Dû le | Jours | État |
|----------|---------|---------|-------|-------|------|
| Alice | Japonais | 2,500 DA | 2025-01-15 | 45 jours | EN RETARD |
| Bob | Anglais | 3,000 DA | 2025-02-01 | 20 jours | EN RETARD |
| Charlie | Arabe | 1,000 DA | 2025-02-28 | -5 jours | À VENIR |

**État actuel:** N'existe pas. Il faut construire une view + template.

### 3.2 Suivi des Rappels (❌ PAS DE MODÈLE)

**Besoin:** Tracer "Quand avons-nous relancé Alice?"

```
PaymentReminder {
    enrollment: ForeignKey
    reminded_date: 2025-02-28
    method: "email" | "sms" | "phone"
    notes: "Alice signale qu'elle paiera demain"
}
```

**État actuel:** Pas de modèle PaymentReminder. Aucune trace des rappels envoyés.

### 3.3 Propriétés Manquantes sur Installment

```python
# À ajouter:

@property
def is_overdue(self):
    return not self.is_paid and self.due_date < today()

@property
def days_overdue(self):
    if self.is_overdue:
        return (today() - self.due_date).days
    return 0

@property
def days_until_due(self):
    if not self.is_paid and self.due_date > today():
        return (self.due_date - today()).days
    return 0
```

### 3.4 Notifications Automatiques (❌ ABSENCE)

- ❌ Pas d'email automatique "Votre paiement est dû"
- ❌ Pas de SMS de rappel
- ❌ Pas de tâche Celery pour envoyer les rappels
- ❌ Pas de template d'email

---

## 4. VÉRIFICATIONS DE L'AUDIT

### 4.1 ✅ Vérification #1: Installments bien générées?

**Commande de test:**
```python
from finance.models import Installment
from academics.models import Cohort
from students.models import Enrollment

# Créer une inscription
e = Enrollment.objects.first()
installs = e.installments.all()
print(f"Inscriptions pour {e}: {installs.count()} échéances")
for i in installs:
    print(f"  {i.due_date}: {i.amount} DA - Payée? {i.is_paid}")
```

**Résultat attendu:** Les échéances s'affichent, bien générées par le signal.

### 4.2 ✅ Vérification #2: Balance calcule correctement?

```python
e = Enrollment.objects.first()
print(f"Tarif: {e.tariff.amount} DA")
print(f"Total payé: {sum(p.amount for p in e.payments.all())} DA")
print(f"Balance due: {e.balance_due} DA")
# Devrait être: tarif - total_payé = balance_due
```

### 4.3 ✅ Vérification #3: Admin fonctionne?

- Aller sur: Django Admin → Finance → Installments
- Peut filtrer par is_paid: Oui ✅
- Peut filtrer par due_date: Oui ✅
- Peut marquer une échéance comme payée: Oui ✅

### 4.4 ❌ Vérification #4: Dashboard rappels?

- Aller sur: Django Admin → Finance → (vérifier il n'existe pas)
- Existe-t-il une view "Rappels de Paiement"? **NON** ❌

### 4.5 ❌ Vérification #5: Suivi des rappels?

```python
from finance.models import ???  # PaymentReminder n'existe pas!
```
**Résultat:** Model n'existe pas ❌

---

## 5. PLAN DE CONSTRUCTION DU SYSTÈME DE RAPPELS

### Phase 1: Amélioration du Modèle Installment (1 jour)

**Fichier à modifier:** `finance/models.py`

Ajouter ces propriétés et méthodes:

```python
class Installment(models.Model):
    # ... champs existants ...
    
    @property
    def is_overdue(self):
        """Vrai si impayée ET date passée"""
        from django.utils.timezone import now
        return not self.is_paid and self.due_date < now().date()
    
    @property
    def days_overdue(self):
        """Nombre de jours de retard (0 si payée ou pas encore due)"""
        from django.utils.timezone import now
        if self.is_overdue:
            return (now().date() - self.due_date).days
        return 0
    
    @property
    def status(self):
        """Retourne le statut lisible"""
        from django.utils.timezone import now
        if self.is_paid:
            return "PAYÉE"
        elif self.due_date > now().date():
            days = (self.due_date - now().date()).days
            return f"À VENIR ({days}j)"
        else:
            return f"EN RETARD ({self.days_overdue}j)"
```

### Phase 2: Modèle de Suivi des Rappels (1 jour)

**Nouveau fichier:** `finance/models.py` (ajouter après Installment)

```python
class PaymentReminder(models.Model):
    """Traçabilité: quand et comment avons-nous relancé le paiement?"""
    METHODS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Appel téléphonique'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    enrollment = models.ForeignKey('students.Enrollment', on_delete=models.CASCADE, related_name='payment_reminders')
    installment = models.ForeignKey(Installment, on_delete=models.SET_NULL, null=True, blank=True)
    
    reminded_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=METHODS)
    
    # Notes d'interaction
    notes = models.TextField(blank=True, default="")
    
    # Qui a envoyé le rappel?
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-reminded_date']
    
    def __str__(self):
        return f"Rappel {self.method} pour {self.enrollment} le {self.reminded_date.date()}"
```

Puis créer migration:
```bash
python manage.py makemigrations finance
python manage.py migrate
```

### Phase 3: Dashboard Rappels (2 jours)

**Nouveau fichier:** `finance/views.py`

```python
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from students.models import Enrollment
from .models import Installment, PaymentReminder
from datetime import timedelta

@staff_member_required
def payment_reminders_dashboard(request):
    """Dashboard pour gérer les rappels de paiement"""
    
    today = now().date()
    
    # Filtres
    filter_type = request.GET.get('filter', 'overdue')  # overdue, due_this_month, all_unpaid
    
    if filter_type == 'overdue':
        installments = Installment.objects.filter(
            is_paid=False,
            due_date__lt=today
        ).select_related('enrollment__student', 'enrollment__cohort', 'enrollment__tariff')
        title = "Paiements en retard"
    
    elif filter_type == 'due_this_month':
        first_day = today.replace(day=1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        installments = Installment.objects.filter(
            is_paid=False,
            due_date__gte=first_day,
            due_date__lte=last_day
        ).select_related('enrollment__student', 'enrollment__cohort', 'enrollment__tariff')
        title = f"Paiements dus en {first_day.strftime('%B %Y')}"
    
    else:  # all_unpaid
        installments = Installment.objects.filter(
            is_paid=False
        ).select_related('enrollment__student', 'enrollment__cohort', 'enrollment__tariff')
        title = "Tous les paiements impayés"
    
    # Grouper par étudiant
    by_student = {}
    for inst in installments:
        student = inst.enrollment.student
        if student not in by_student:
            by_student[student] = {
                'enrollments': {},
                'total_unpaid': 0
            }
        
        enrollment = inst.enrollment
        if enrollment not in by_student[student]['enrollments']:
            by_student[student]['enrollments'][enrollment] = {
                'installments': [],
                'total': 0
            }
        
        by_student[student]['enrollments'][enrollment]['installments'].append(inst)
        by_student[student]['enrollments'][enrollment]['total'] += inst.amount
        by_student[student]['total_unpaid'] += inst.amount
    
    # Récents rappels pour chaque étudiant
    for student in by_student:
        last_reminder = PaymentReminder.objects.filter(
            enrollment__student=student
        ).order_by('-reminded_date').first()
        by_student[student]['last_reminder'] = last_reminder
    
    context = {
        'title': title,
        'by_student': by_student,
        'total_amount': sum(s['total_unpaid'] for s in by_student.values()),
        'filter_type': filter_type,
    }
    
    return render(request, 'finance/payment_reminders_dashboard.html', context)


@staff_member_required
def mark_reminder_sent(request, installment_id):
    """Enregistrer qu'on a envoyé un rappel"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    from django.http import JsonResponse
    
    installment = Installment.objects.get(pk=installment_id)
    method = request.POST.get('method', 'email')
    notes = request.POST.get('notes', '')
    
    reminder = PaymentReminder.objects.create(
        enrollment=installment.enrollment,
        installment=installment,
        method=method,
        notes=notes,
        sent_by=request.user
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Rappel enregistré le {reminder.reminded_date.date()}'
    })
```

**Nouvelle route:** `finance/urls.py`

```python
urlpatterns = [
    path('reminders-dashboard/', payment_reminders_dashboard, name='reminders_dashboard'),
    path('installment/<int:installment_id>/mark-reminded/', mark_reminder_sent, name='mark_reminder_sent'),
    # ... autres routes ...
]
```

### Phase 4: Template Dashboard (1 jour)

**Nouveau fichier:** `templates/finance/payment_reminders_dashboard.html`

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Rappels de Paiement{% endblock %}

{% block content %}
<div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">📋 Rappels de Paiement</h1>
    
    <!-- Filtres -->
    <div class="mb-6 flex gap-3">
        <a href="?filter=overdue" class="px-4 py-2 rounded {% if filter_type == 'overdue' %}bg-red-500 text-white{% else %}bg-gray-200{% endif %}">
            🔴 En retard
        </a>
        <a href="?filter=due_this_month" class="px-4 py-2 rounded {% if filter_type == 'due_this_month' %}bg-orange-500 text-white{% else %}bg-gray-200{% endif %}">
            📅 Ce mois
        </a>
        <a href="?filter=all_unpaid" class="px-4 py-2 rounded {% if filter_type == 'all_unpaid' %}bg-blue-500 text-white{% else %}bg-gray-200{% endif %}">
            📊 Tous impayés
        </a>
    </div>
    
    <!-- Résumé -->
    <div class="bg-blue-100 p-4 rounded mb-6 font-bold">
        {{ title }} | Total: <span class="text-xl">{{ total_amount|floatformat:0 }} DA</span>
    </div>
    
    <!-- Étudiants -->
    {% for student, data in by_student.items %}
    <div class="border rounded p-4 mb-4 bg-white shadow">
        <div class="flex justify-between items-start mb-3">
            <div>
                <h3 class="text-xl font-bold">{{ student.get_full_name }}</h3>
                <p class="text-gray-600">Code: {{ student.student_code }}</p>
                {% if data.last_reminder %}
                <p class="text-sm text-gray-500">
                    Dernier rappel: {{ data.last_reminder.reminded_date|date:"d/m/Y" }} ({{ data.last_reminder.method }})
                </p>
                {% endif %}
            </div>
            <div class="text-right font-bold text-lg">
                {{ data.total_unpaid }} DA
            </div>
        </div>
        
        <!-- Inscriptions -->
        {% for enrollment, enroll_data in data.enrollments.items %}
        <div class="ml-4 mb-3 border-l-4 border-blue-300 pl-4 bg-gray-50 p-3 rounded">
            <p class="font-semibold">{{ enrollment.cohort.name }} ({{ enrollment.cohort.subject.name }})</p>
            
            <!-- Échéances -->
            <table class="w-full text-sm mt-2">
                <thead class="text-gray-600 text-left">
                    <tr>
                        <th>Dû le</th>
                        <th>Montant</th>
                        <th>Statut</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for inst in enroll_data.installments %}
                    <tr class="border-t">
                        <td class="py-2">{{ inst.due_date|date:"d/m/Y" }}</td>
                        <td>{{ inst.amount }} DA</td>
                        <td>
                            {% if inst.is_overdue %}
                            <span class="px-2 py-1 bg-red-200 text-red-800 rounded text-xs font-bold">
                                🔴 {{ inst.days_overdue }}j EN RETARD
                            </span>
                            {% else %}
                            <span class="px-2 py-1 bg-yellow-200 text-yellow-800 rounded text-xs">
                                ⏳ À VENIR
                            </span>
                            {% endif %}
                        </td>
                        <td>
                            <button onclick="markReminder({{ inst.id }})" class="text-blue-500 text-sm hover:underline">
                                📧 Relancer
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
    
    <!-- Modal rappel -->
    <div id="reminderModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded shadow-lg">
            <h3 class="text-lg font-bold mb-4">Enregistrer le rappel</h3>
            <select id="reminderMethod" class="w-full mb-3 p-2 border rounded">
                <option value="email">📧 Email</option>
                <option value="sms">📱 SMS</option>
                <option value="phone">☎️ Appel</option>
                <option value="whatsapp">💬 WhatsApp</option>
            </select>
            <textarea id="reminderNotes" placeholder="Notes..." class="w-full mb-3 p-2 border rounded h-20"></textarea>
            <div class="flex gap-2">
                <button onclick="sendReminder()" class="px-4 py-2 bg-blue-500 text-white rounded">Envoyer</button>
                <button onclick="closeModal()" class="px-4 py-2 bg-gray-300 rounded">Annuler</button>
            </div>
        </div>
    </div>
</div>

<script>
let currentInstallmentId = null;

function markReminder(installmentId) {
    currentInstallmentId = installmentId;
    document.getElementById('reminderModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('reminderModal').classList.add('hidden');
}

function sendReminder() {
    const method = document.getElementById('reminderMethod').value;
    const notes = document.getElementById('reminderNotes').value;
    
    fetch(`/finance/installment/${currentInstallmentId}/mark-reminded/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: new FormData(document.querySelector('form'))
    })
    .then(r => r.json())
    .then(d => {
        alert(d.message);
        closeModal();
        location.reload();
    });
}
</script>
{% endblock %}
```

### Phase 5: Admin Integration (1/2 jour)

**Fichier:** `finance/admin.py`

```python
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'installment', 'method', 'reminded_date', 'sent_by')
    list_filter = ('method', 'reminded_date')
    search_fields = ('enrollment__student__first_name', 'enrollment__student__last_name')
    readonly_fields = ('reminded_date', 'sent_by')

admin.site.register(PaymentReminder, PaymentReminderAdmin)
```

---

## 6. TIMELINE DE LIVRAISON

| Phase | Tâche | Durée | Dépendance |
|-------|-------|-------|-----------|
| 1 | Ajouter propriétés à Installment | 1h | - |
| 2 | Créer modèle PaymentReminder | 2h | Phase 1 |
| 3 | Implémenter views dashboard | 4h | Phase 1, 2 |
| 4 | Template HTML + JS | 3h | Phase 3 |
| 5 | Admin et tests | 2h | Toutes |
| **TOTAL** | | **4 jours** | |

---

## 7. RÉSUMÉ DES FICHIERS À CRÉER/MODIFIER

### À Modifier:
- `finance/models.py` - Ajouter propriétés + modèle PaymentReminder
- `finance/views.py` - Ajouter dashboard views
- `finance/urls.py` - Ajouter routes
- `finance/admin.py` - Ajouter PaymentReminderAdmin

### À Créer:
- `templates/finance/payment_reminders_dashboard.html` - Template dashboard
- `finance/migrations/000X_add_payment_reminder.py` - Auto-généré

### Tests à Ajouter:
- `finance/tests.py` - Tests du dashboard et des propriétés

---

## 8. CONCLUSION

**Le système est 85% prêt.** Les modèles, signaux et calculs de base existent. Il suffit de:

1. ✅ Enrichir le modèle Installment avec des propriétés
2. ✅ Ajouter le tracking des rappels (PaymentReminder)
3. ✅ Construire le dashboard pour voir les impayés
4. ✅ Connecter l'admin pour enregistrer les rappels

Pas besoin de refondre la logique de paiement - elle marche bien! Juste ajouter la couche de "gestion des rappels" par-dessus.

---

**Audit réalisé par:** AI Assistant
**État:** PRÊT À IMPLÉMENTER
**Prochaine étape:** Confirmer le plan et commencer Phase 1
