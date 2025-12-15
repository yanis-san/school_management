# core/views.py
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from academics.models import CourseSession
from students.models import Enrollment
from finance.models import Payment

def dashboard(request):
    today = timezone.now().date()
    
    # 1. Les cours du jour (Triés par heure)
    todays_sessions = CourseSession.objects.filter(
        date=today
    ).select_related('cohort', 'teacher', 'classroom').order_by('start_time')

    # 2. Quelques chiffres clés
    total_students = Enrollment.objects.filter(is_active=True).count()
    
    # Chiffre d'affaire du mois
    monthly_income = Payment.objects.filter(
        date__month=today.month, 
        date__year=today.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'sessions': todays_sessions,
        'total_students': total_students,
        'monthly_income': monthly_income,
        'today': today,
    }
    return render(request, 'core/dashboard.html', context)