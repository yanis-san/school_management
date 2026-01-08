# core/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from academics.models import CourseSession, Cohort
from students.models import Enrollment, StudentAnnualFee
from finance.models import Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import User, AcademicYear

@login_required
def dashboard(request):
    today = timezone.now().date()
    user = request.user

    # Vérifier si l'utilisateur est un professeur
    is_teacher = user.is_authenticated and user.is_teacher

    if is_teacher:
        # DASHBOARD PROFESSEUR : Voir TOUTES ses séances (titulaire OU remplaçant)
        todays_sessions = CourseSession.objects.filter(
            teacher=user,  # Toutes les séances où il est le prof (titulaire ou remplaçant)
            date=today
        ).select_related('cohort', 'classroom', 'teacher').order_by('start_time')

        # Ses groupes actifs : cohorts où il est titulaire OU où il a au moins une séance
        cohorts_as_teacher = Cohort.objects.filter(teacher=user)
        cohort_ids_with_sessions = CourseSession.objects.filter(
            teacher=user
        ).values_list('cohort_id', flat=True).distinct()
        my_cohorts = Cohort.objects.filter(
            id__in=list(cohorts_as_teacher.values_list('id', flat=True)) + list(cohort_ids_with_sessions)
        ).prefetch_related('enrollments__student').order_by('name').distinct()

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

        # Année académique courante
        current_year = AcademicYear.get_current()

        # Filtres depuis la requête GET
        filter_year = request.GET.get('year')  # ID de l'année académique
        filter_period = request.GET.get('period', 'academic_year')  # 'month', 'quarter', 'academic_year'
        filter_language = request.GET.get('language')  # ID du Subject (langue)
        filter_modality = request.GET.get('modality')  # 'ONLINE', 'IN_PERSON'
        filter_type = request.GET.get('type')  # 'individual', 'group'

        # Par défaut, utiliser l'année académique courante
        if not filter_year and current_year:
            filter_year = str(current_year.id)

        # Récupérer l'année sélectionnée
        selected_year = None
        if filter_year:
            try:
                selected_year = AcademicYear.objects.get(id=int(filter_year))
            except:
                selected_year = current_year

        # Calcul des revenus selon le filtre
        from django.db.models import Q
        from datetime import datetime, timedelta
        from academics.models import Subject

        # Revenus par année académique
        academic_year_income = 0
        monthly_income = 0
        quarterly_data = {}
        languages_income = {}  # {language_name: income}
        modality_income = {}   # {'Présentiel': X, 'En ligne': Y}
        type_income = {}       # {'Groupe': X, 'Individuel': Y}

        if selected_year:
            # Déterminer la clause de filtre pour la langue
            language_filter = Q()
            if filter_language:
                try:
                    language_obj = Subject.objects.get(id=int(filter_language))
                    language_filter = Q(enrollment__cohort__subject=language_obj)
                except:
                    pass

            # Déterminer la clause de filtre pour la modalité
            modality_filter = Q()
            if filter_modality:
                modality_filter = Q(enrollment__cohort__modality=filter_modality)

            # Déterminer la clause de filtre pour le type
            type_filter = Q()
            if filter_type == 'individual':
                type_filter = Q(enrollment__cohort__is_individual=True)
            elif filter_type == 'group':
                type_filter = Q(enrollment__cohort__is_individual=False)

            # Combiner tous les filtres
            combined_filter = language_filter & modality_filter & type_filter

            # Revenus de toute l'année académique
            academic_year_income = Payment.objects.filter(
                date__gte=selected_year.start_date,
                date__lte=selected_year.end_date
            ).filter(combined_filter).aggregate(Sum('amount'))['amount__sum'] or 0

            # Revenus par langue
            all_languages = Subject.objects.all().order_by('name')
            for lang in all_languages:
                lang_income = Payment.objects.filter(
                    date__gte=selected_year.start_date,
                    date__lte=selected_year.end_date,
                    enrollment__cohort__subject=lang
                ).filter(modality_filter & type_filter).aggregate(Sum('amount'))['amount__sum'] or 0
                if lang_income > 0:
                    languages_income[lang.name] = float(lang_income)

            # Revenus par modalité
            for modality_key, modality_label in [('IN_PERSON', 'Présentiel'), ('ONLINE', 'En ligne')]:
                modality_rev = Payment.objects.filter(
                    date__gte=selected_year.start_date,
                    date__lte=selected_year.end_date,
                    enrollment__cohort__modality=modality_key
                ).filter(language_filter & type_filter).aggregate(Sum('amount'))['amount__sum'] or 0
                if modality_rev > 0:
                    modality_income[modality_label] = float(modality_rev)

            # Revenus par type
            for is_ind, type_label in [(True, 'Individuel'), (False, 'Groupe')]:
                type_rev = Payment.objects.filter(
                    date__gte=selected_year.start_date,
                    date__lte=selected_year.end_date,
                    enrollment__cohort__is_individual=is_ind
                ).filter(language_filter & modality_filter).aggregate(Sum('amount'))['amount__sum'] or 0
                if type_rev > 0:
                    type_income[type_label] = float(type_rev)

            # Revenus par mois de l'année académique
            monthly_breakdown = []
            current_date = selected_year.start_date
            while current_date <= selected_year.end_date:
                month_end = current_date.replace(day=1) + timedelta(days=32)
                month_end = month_end.replace(day=1) - timedelta(days=1)
                if month_end > selected_year.end_date:
                    month_end = selected_year.end_date

                month_income = Payment.objects.filter(
                    date__gte=current_date,
                    date__lte=month_end
                ).filter(language_filter).aggregate(Sum('amount'))['amount__sum'] or 0

                month_name = current_date.strftime('%B %Y')
                monthly_breakdown.append({
                    'name': month_name,
                    'value': float(month_income),
                    'date': current_date.strftime('%Y-%m')
                })

                current_date = month_end + timedelta(days=1)

            # Revenus par trimestre
            quarterly_data = {
                'Q1': 0,  # Sept-Nov
                'Q2': 0,  # Déc-Fév
                'Q3': 0,  # Mar-Mai
                'Q4': 0,  # Juin-Août
            }

            for payment in Payment.objects.filter(
                date__gte=selected_year.start_date,
                date__lte=selected_year.end_date
            ).filter(language_filter):
                month = payment.date.month
                # Déterminer le trimestre (année académique 9-8)
                if month in [9, 10, 11]:
                    quarterly_data['Q1'] += float(payment.amount)
                elif month in [12, 1, 2]:
                    quarterly_data['Q2'] += float(payment.amount)
                elif month in [3, 4, 5]:
                    quarterly_data['Q3'] += float(payment.amount)
                else:  # 6, 7, 8
                    quarterly_data['Q4'] += float(payment.amount)

            # Revenu du mois actuel (pour info)
            monthly_income = Payment.objects.filter(
                date__month=today.month,
                date__year=today.year
            ).filter(language_filter).aggregate(Sum('amount'))['amount__sum'] or 0
        else:
            monthly_breakdown = []

        # Calcul des frais d'inscription pour l'année sélectionnée
        registration_fees_total = 0
        paid_registrations_count = 0
        if selected_year:
            paid_registrations = StudentAnnualFee.objects.filter(
                academic_year=selected_year,
                is_paid=True
            )
            paid_registrations_count = paid_registrations.count()
            registration_fees_total = paid_registrations_count * selected_year.registration_fee_amount

        # Liste de toutes les années académiques pour le filtre
        all_academic_years = AcademicYear.objects.all().order_by('-start_date')
        
        # Liste de toutes les langues (subjects)
        all_languages = Subject.objects.all().order_by('name')

        context = {
            'is_teacher': False,
            'sessions': todays_sessions,
            'total_students': total_students,
            'monthly_income': monthly_income,
            'academic_year_income': academic_year_income,
            'registration_fees_total': registration_fees_total,
            'paid_registrations_count': paid_registrations_count,
            'current_academic_year': current_year,
            'selected_year': selected_year,
            'all_academic_years': all_academic_years,
            'all_languages': all_languages,
            'filter_language': filter_language,
            'filter_modality': filter_modality,
            'filter_type': filter_type,
            'languages_income': languages_income,
            'modality_income': modality_income,
            'type_income': type_income,
            'filter_period': filter_period,
            'monthly_breakdown': monthly_breakdown,
            'quarterly_data': quarterly_data,
            'today': today,
        }

    return render(request, 'core/dashboard.html', context)


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
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


@login_required
def academic_year_list(request):
    """Liste les années scolaires avec possibilité d'ajouter/modifier/activer"""
    from .models import AcademicYear
    from django.http import JsonResponse
    
    years = AcademicYear.objects.all().order_by('-label')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            label = request.POST.get('label', '').strip()
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            is_current = request.POST.get('is_current') == 'on'
            
            if not label or not start_date or not end_date:
                return JsonResponse({'success': False, 'error': 'Tous les champs sont obligatoires'}, status=400)
            
            try:
                AcademicYear.objects.create(
                    label=label,
                    start_date=start_date,
                    end_date=end_date,
                    is_current=is_current
                )
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
        elif action == 'edit':
            year_id = request.POST.get('year_id')
            label = request.POST.get('label', '').strip()
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            if not label or not start_date or not end_date:
                return JsonResponse({'success': False, 'error': 'Tous les champs sont obligatoires'}, status=400)
            
            try:
                year = AcademicYear.objects.get(pk=year_id)
                year.label = label
                year.start_date = start_date
                year.end_date = end_date
                year.save()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
        elif action == 'set_current':
            year_id = request.POST.get('year_id')
            try:
                year = AcademicYear.objects.get(pk=year_id)
                year.is_current = True
                year.save()  # save() déclenche la logique pour désactiver les autres
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
        elif action == 'delete':
            year_id = request.POST.get('year_id')
            try:
                year = AcademicYear.objects.get(pk=year_id)
                year.delete()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    context = {'years': years}
    return render(request, 'core/academic_year_list.html', context)