# core/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from academics.models import CourseSession, Cohort
from students.models import Enrollment
from finance.models import Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import User

@login_required
def dashboard(request):
    today = timezone.now().date()
    user = request.user

    # Vérifier si l'utilisateur est un professeur
    is_teacher = user.is_authenticated and user.is_teacher

    if is_teacher:
        # DASHBOARD PROFESSEUR : Voir uniquement SES cours et SES groupes
        todays_sessions = CourseSession.objects.filter(
            teacher=user,
            date=today
        ).select_related('cohort', 'classroom').order_by('start_time')

        # Ses groupes actifs
        my_cohorts = Cohort.objects.filter(
            teacher=user
        ).prefetch_related('enrollments__student').order_by('name')

        # Statistiques personnelles
        my_total_students = Enrollment.objects.filter(
            cohort__teacher=user,
            is_active=True
        ).count()

        # Nombre de séances complétées ce mois
        completed_this_month = CourseSession.objects.filter(
            teacher=user,
            status='COMPLETED',
            date__month=today.month,
            date__year=today.year
        ).count()

        context = {
            'is_teacher': True,
            'sessions': todays_sessions,
            'my_cohorts': my_cohorts,
            'total_students': my_total_students,
            'completed_this_month': completed_this_month,
            'today': today,
        }
    else:
        # DASHBOARD ADMIN : Voir TOUT
        todays_sessions = CourseSession.objects.filter(
            date=today
        ).select_related('cohort', 'teacher', 'classroom').order_by('start_time')

        # Chiffres globaux
        total_students = Enrollment.objects.filter(is_active=True).count()

        # Chiffre d'affaire du mois
        monthly_income = Payment.objects.filter(
            date__month=today.month,
            date__year=today.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        context = {
            'is_teacher': False,
            'sessions': todays_sessions,
            'total_students': total_students,
            'monthly_income': monthly_income,
            'today': today,
        }

    return render(request, 'core/dashboard.html', context)


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username} !')

            # Rediriger vers la page demandée ou le dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect.')

    return render(request, 'core/login.html')


def signup_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        is_teacher = request.POST.get('is_teacher') == 'on'

        # Validation
        if password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        else:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_teacher=is_teacher
            )

            messages.success(request, 'Compte créé avec succès ! Vous pouvez maintenant vous connecter.')
            return redirect('login')

    return render(request, 'core/signup.html')


def logout_view(request):
    """Vue de déconnexion"""
    auth_logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')