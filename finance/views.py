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


# =====================================================
# GESTION DE LA PAIE DES PROFESSEURS (PAYROLL SYSTEM)
# =====================================================

from django.db.models import Sum, F, ExpressionWrapper, DurationField
from datetime import datetime, timedelta, date
from core.models import User, TeacherProfile
from academics.models import CourseSession
from .models import TeacherPayment
from django.contrib import messages


def teacher_payroll_list(request):
    """
    Vue principale : Liste des professeurs avec calcul de la paie due.
    Affiche pour chaque prof : heures travaillées, montant dû, méthode préférée.
    """
    # Récupérer tous les professeurs
    teachers = User.objects.filter(is_teacher=True).select_related('teacher_profile')

    # Récupérer les filtres de période (par défaut : mois dernier)
    today = date.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    period_start = request.GET.get('start', first_day_last_month.strftime('%Y-%m-%d'))
    period_end = request.GET.get('end', last_day_last_month.strftime('%Y-%m-%d'))

    # Convertir en date objects
    period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
    period_end = datetime.strptime(period_end, '%Y-%m-%d').date()

    payroll_data = []

    for teacher in teachers:
        # Récupérer les séances COMPLETED pour cette période
        sessions = CourseSession.objects.filter(
            teacher=teacher,
            status='COMPLETED',
            date__gte=period_start,
            date__lte=period_end
        ).select_related('cohort')

        # Calculer les heures travaillées et le montant total
        total_hours = 0
        total_amount = 0

        for session in sessions:
            # Calculer la durée de la séance en heures décimales
            duration = datetime.combine(date.today(), session.end_time) - datetime.combine(date.today(), session.start_time)
            hours = duration.total_seconds() / 3600

            # Montant pour cette séance
            session_pay = hours * float(session.cohort.teacher_hourly_rate)

            total_hours += hours
            total_amount += session_pay

        # Vérifier si déjà payé pour cette période
        already_paid = TeacherPayment.objects.filter(
            teacher=teacher,
            period_start=period_start,
            period_end=period_end
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Récupérer le profil (ou None si pas créé)
        profile = getattr(teacher, 'teacher_profile', None)

        payroll_data.append({
            'teacher': teacher,
            'profile': profile,
            'total_hours': round(total_hours, 2),
            'total_amount': round(total_amount, 2),
            'already_paid': float(already_paid),
            'balance_due': round(total_amount - float(already_paid), 2),
            'sessions_count': sessions.count(),
        })

    context = {
        'payroll_data': payroll_data,
        'period_start': period_start,
        'period_end': period_end,
    }
    return render(request, 'finance/teacher_payroll_list.html', context)


def teacher_payroll_detail(request, teacher_id):
    """
    Détail d'un professeur : historique des paiements + séances de la période actuelle.
    """
    teacher = get_object_or_404(User, id=teacher_id, is_teacher=True)

    # Récupérer la période depuis les paramètres GET
    today = date.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    period_start = request.GET.get('start', first_day_last_month.strftime('%Y-%m-%d'))
    period_end = request.GET.get('end', last_day_last_month.strftime('%Y-%m-%d'))

    period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
    period_end = datetime.strptime(period_end, '%Y-%m-%d').date()

    # Récupérer les séances complétées pour cette période
    sessions = CourseSession.objects.filter(
        teacher=teacher,
        status='COMPLETED',
        date__gte=period_start,
        date__lte=period_end
    ).select_related('cohort', 'classroom').order_by('date', 'start_time')

    # Calculer le détail
    session_details = []
    total_hours = 0
    total_amount = 0

    for session in sessions:
        duration = datetime.combine(date.today(), session.end_time) - datetime.combine(date.today(), session.start_time)
        hours = duration.total_seconds() / 3600
        pay = hours * float(session.cohort.teacher_hourly_rate)

        session_details.append({
            'session': session,
            'hours': round(hours, 2),
            'hourly_rate': float(session.cohort.teacher_hourly_rate),
            'pay': round(pay, 2),
        })

        total_hours += hours
        total_amount += pay

    # Historique des paiements (tous)
    payment_history = TeacherPayment.objects.filter(teacher=teacher).order_by('-payment_date')

    # Profil du prof
    profile = getattr(teacher, 'teacher_profile', None)

    context = {
        'teacher': teacher,
        'profile': profile,
        'period_start': period_start,
        'period_end': period_end,
        'session_details': session_details,
        'total_hours': round(total_hours, 2),
        'total_amount': round(total_amount, 2),
        'payment_history': payment_history,
    }
    return render(request, 'finance/teacher_payroll_detail.html', context)


def record_teacher_payment(request, teacher_id):
    """
    Formulaire pour enregistrer un paiement de salaire.
    Pré-remplit avec la méthode préférée du prof et le montant dû.
    """
    teacher = get_object_or_404(User, id=teacher_id, is_teacher=True)

    # Récupérer la période depuis les paramètres GET
    today = date.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    period_start_str = request.GET.get('start', first_day_last_month.strftime('%Y-%m-%d'))
    period_end_str = request.GET.get('end', last_day_last_month.strftime('%Y-%m-%d'))
    amount_due = request.GET.get('amount', '0')

    if request.method == 'POST':
        try:
            # Créer le paiement
            payment = TeacherPayment.objects.create(
                teacher=teacher,
                period_start=datetime.strptime(request.POST.get('period_start'), '%Y-%m-%d').date(),
                period_end=datetime.strptime(request.POST.get('period_end'), '%Y-%m-%d').date(),
                total_amount=request.POST.get('total_amount'),
                payment_method=request.POST.get('payment_method'),
                payment_date=datetime.strptime(request.POST.get('payment_date'), '%Y-%m-%d').date(),
                recorded_by=request.user,
                proof_reference=request.POST.get('proof_reference', ''),
                notes=request.POST.get('notes', ''),
            )

            messages.success(request, f"Paiement de {payment.total_amount} DA enregistré avec succès pour {teacher.get_full_name()}!")
            return redirect('finance:teacher_payroll_list')

        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement : {str(e)}")

    # Récupérer le profil pour la méthode préférée
    profile = getattr(teacher, 'teacher_profile', None)
    preferred_method = profile.preferred_payment_method if profile else 'CASH'

    context = {
        'teacher': teacher,
        'profile': profile,
        'period_start': period_start_str,
        'period_end': period_end_str,
        'amount_due': amount_due,
        'preferred_method': preferred_method,
        'today': today.strftime('%Y-%m-%d'),
    }
    return render(request, 'finance/record_teacher_payment.html', context)