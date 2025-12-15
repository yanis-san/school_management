from django.shortcuts import render

def apply_group_discount(cohort_id, discount_id):
    """Applique une réduction à TOUS les étudiants d'un groupe"""
    cohort = Cohort.objects.get(id=cohort_id)
    discount = Discount.objects.get(id=discount_id)
    
    enrollments = Enrollment.objects.filter(cohort=cohort, is_active=True)
    
    for enrollment in enrollments:
        enrollment.discount = discount
        # On force le recalcul (en remettant agreed_amount à None ou via une méthode update)
        # Attention : Si l'étudiant a déjà payé, c'est délicat. 
        # Ici on suppose qu'on applique ça au début.
        
        base = cohort.standard_price
        if discount.type == 'FIXED':
            new_price = base - discount.value
        else:
            new_price = base - (base * (discount.value / 100))
            
        enrollment.agreed_amount = new_price
        enrollment.save()



from django.shortcuts import render, redirect, get_object_or_404
from students.models import Enrollment
from .forms import PaymentForm

def add_payment(request, enrollment_id):
    # On récupère le contrat spécifique (ex: Chinois de Lina)
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.enrollment = enrollment
            payment.recorded_by = request.user # L'admin connecté
            payment.save()
            
            # Une fois payé, on retourne sur la fiche de l'élève
            return redirect('students:detail', pk=enrollment.student.id)
    else:
        # On pré-remplit avec le reste à payer (Balance Due)
        form = PaymentForm(initial={'amount': enrollment.balance_due})

    context = {
        'form': form,
        'enrollment': enrollment,
        'student': enrollment.student
    }
    return render(request, 'finance/payment_form.html', context)