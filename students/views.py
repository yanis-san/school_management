# students/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Student, Enrollment, StudentAnnualFee
from core.models import AcademicYear
from academics.models import Cohort
from finance.models import Discount, Tariff
from django.contrib import messages
import csv
from django.utils.timezone import now
from datetime import date
import uuid


def generate_unique_student_code(phone=None):
    """
    Génère un code étudiant unique basé sur l'année scolaire actuelle.
    Format: YYYYYYYYNNNNNN (ex: 202520260001)
    Crée une année scolaire par défaut si aucune n'existe.
    """
    academic_year = AcademicYear.get_current()
    
    if not academic_year:
        # Créer une année scolaire par défaut
        from datetime import datetime
        current_year = datetime.now().year
        default_label = f"{current_year}-{current_year + 1}"
        
        # Chercher une année existante avec ce label
        academic_year = AcademicYear.objects.filter(label=default_label).first()
        
        if not academic_year:
            # Créer une année par défaut et la marquer comme actuelle
            academic_year = AcademicYear.objects.create(
                label=default_label,
                start_date=date(current_year, 9, 1),  # Sept 1er
                end_date=date(current_year + 1, 8, 31),  # 31 Août
                is_current=True
            )
    
    # Parse le label pour obtenir les années (ex: "2025-2026")
    years = academic_year.label.split('-')
    if len(years) == 2:
        year_label = f"{years[0]}{years[1]}"
    else:
        year_label = academic_year.label.replace('-', '')
    
    # Trouver le prochain numéro de séquence pour cette année
    # On cherche les codes commençant par l'année actuelle
    last_student = Student.objects.filter(
        student_code__startswith=year_label
    ).order_by('-student_code').first()
    
    if last_student and last_student.student_code:
        try:
            # Extraire le numéro de séquence (6 derniers chiffres)
            last_seq = int(last_student.student_code[-6:])
            next_seq = last_seq + 1
        except (ValueError, IndexError):
            next_seq = 1
    else:
        next_seq = 1
    
    # Générer le code avec séquence 6 chiffres
    return f"{year_label}{next_seq:06d}"

def enrollment_form(request):
    """Retourne le formulaire d'inscription (modal HTML)"""
    student_id = request.GET.get('student_id')
    student = None
    
    if student_id:
        # Réinscription d'un étudiant existant
        student = get_object_or_404(Student, pk=student_id)
    
    context = {
        'cohorts': Cohort.objects.filter(schedule_generated=True),
        'discounts': Discount.objects.filter(is_active=True),
        'tariffs': Tariff.objects.all(),
        'student': student,  # None si nouvelle inscription, objet Student si réinscription
    }
    return render(request, 'students/enrollment_form.html', context)


def create_enrollment(request):
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone')
            sex = request.POST.get('sex', '') or ''
            birth_date = request.POST.get('birth_date') or None
            student_id = request.POST.get('student_id')

            profile_picture = request.FILES.get('profile_picture')
            id_card_front = request.FILES.get('id_card_front')
            id_card_back = request.FILES.get('id_card_back')

            # 1. Récupérer ou créer l'élève de manière sûre (éviter doublons)
            if student_id:
                # Réinscription: on référence directement l'élève par son ID
                student = get_object_or_404(Student, pk=student_id)
                # Mettre à jour les champs éditables (phone reste tel quel car readonly sur le formulaire)
                student.first_name = request.POST.get('first_name')
                student.last_name = request.POST.get('last_name')
                if sex:
                    student.sex = sex
                student.email = request.POST.get('email')
                student.phone_2 = request.POST.get('phone_2', '')
                student.birth_date = birth_date
                student.motivation = request.POST.get('motivation', '')
                if profile_picture:
                    student.profile_picture = profile_picture
                if id_card_front:
                    student.id_card_front = id_card_front
                if id_card_back:
                    student.id_card_back = id_card_back
                student.save()
            else:
                # Nouveau ou récupération par téléphone
                student = Student.objects.filter(phone=phone).first()
                if student:
                    # Mettre à jour si trouvé par téléphone
                    student.first_name = request.POST.get('first_name')
                    student.last_name = request.POST.get('last_name')
                    if sex:
                        student.sex = sex
                    student.email = request.POST.get('email')
                    student.phone_2 = request.POST.get('phone_2', '')
                    student.birth_date = birth_date
                    student.motivation = request.POST.get('motivation', '')
                    # Ne pas écraser le code s'il existe déjà
                    if not student.student_code:
                        student.student_code = generate_unique_student_code()
                    if profile_picture:
                        student.profile_picture = profile_picture
                    if id_card_front:
                        student.id_card_front = id_card_front
                    if id_card_back:
                        student.id_card_back = id_card_back
                    student.save()
                else:
                    # Création d'un nouvel élève
                    student = Student.objects.create(
                        first_name=request.POST.get('first_name'),
                        last_name=request.POST.get('last_name'),
                        sex=sex,
                        email=request.POST.get('email'),
                        phone=phone,
                        phone_2=request.POST.get('phone_2', ''),
                        birth_date=birth_date,
                        motivation=request.POST.get('motivation', ''),
                        student_code=generate_unique_student_code(),
                        profile_picture=profile_picture if profile_picture else None,
                        id_card_front=id_card_front if id_card_front else None,
                        id_card_back=id_card_back if id_card_back else None,
                    )

            # 2. Vérifier si une cohort a été sélectionnée
            cohort_id = request.POST.get('cohort_id')
            
            # 3. Gestion du Discount (peut être vide/None)
            discount_id = request.POST.get('discount_id')
            discount_obj = None
            if discount_id:
                discount_obj = Discount.objects.get(id=discount_id)

            # 4. Si pas de cohort, créer seulement l'étudiant
            if not cohort_id:
                messages.success(request, f"Étudiant {student.first_name} {student.last_name} créé avec succès ! Vous pouvez l'inscrire à un groupe plus tard.")
                response = HttpResponse()
                response['HX-Refresh'] = "true"
                return response
            
            # 5. Si cohort spécifiée, créer l'inscription
            cohort = Cohort.objects.get(id=cohort_id)
            tariff_id = request.POST.get('tariff_id')
            
            if tariff_id:
                # L'utilisateur a sélectionné un tarif
                tariff = Tariff.objects.get(id=tariff_id)
            else:
                # Pas de tarif sélectionné : utiliser le prix standard du groupe
                tariff_name = f"Tarif {cohort.name}"
                tariff, created = Tariff.objects.get_or_create(
                    name=tariff_name,
                    defaults={'amount': cohort.standard_price}
                )

            # 6. Création de l'inscription (nouveau contrat)
            Enrollment.objects.create(
                student=student,
                cohort=cohort,
                tariff=tariff,
                discount=discount_obj,
                payment_plan=request.POST.get('payment_plan')
            )
            
            # Feedback et Rafraîchissement
            messages.success(request, f"Inscription réussie pour {student.first_name} !")
            
            response = HttpResponse()
            response['HX-Refresh'] = "true" # Commande HTMX pour recharger la page proprement
            return response

        except Exception as e:
            # En cas d'erreur, on affiche une notification rouge flottante
            return HttpResponse(f"<div class='fixed top-5 right-5 bg-red-500 text-white p-4 rounded shadow-lg z-50'>Erreur: {str(e)}</div>")
        



from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from .models import Student
from academics.models import Cohort

def student_list(request):
    # 1. Récupération des paramètres GET (ce qu'il y a dans l'URL ?q=yanis&cohort=1)
    search_query = request.GET.get('q', '')
    cohort_filter = request.GET.get('cohort', '')

    # 2. Requête de base optimisée
    students = Student.objects.prefetch_related(
        Prefetch(
            'enrollments',
            queryset=Enrollment.objects.filter(is_active=True).select_related('cohort', 'tariff'),
            to_attr='active_enrollments'
        )
    ).all().order_by('-created_at')

    # 3. Application de la Recherche (Si l'utilisateur a tapé quelque chose)
    if search_query:
        students = students.filter(
            Q(last_name__icontains=search_query) | 
            Q(first_name__icontains=search_query) |
            Q(student_code__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # 4. Application du Filtre par Classe (Si une classe est sélectionnée)
    if cohort_filter:
        students = students.filter(enrollments__cohort__id=cohort_filter)

    # 5. Pagination (20 étudiants par page max)
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 6. On récupère toutes les cohortes pour remplir la liste déroulante du filtre
    all_cohorts = Cohort.objects.filter(academic_year__is_current=True)

    # Année académique active et frais payés (pour afficher un badge)
    current_year = AcademicYear.get_current()
    paid_ids = set()
    if current_year:
        try:
            paid_ids = set(
                StudentAnnualFee.objects.filter(
                    academic_year=current_year,
                    is_paid=True,
                    student__in=page_obj.object_list
                ).values_list('student_id', flat=True)
            )
        except Exception:
            paid_ids = set()

    context = {
        'students': page_obj, # On passe la page, pas toute la liste
        'search_query': search_query,
        'cohort_filter': int(cohort_filter) if cohort_filter else '',
        'all_cohorts': all_cohorts,
        'annual_fee_paid_ids': paid_ids,
        'current_academic_year': current_year,
    }
    
    # Si requête HTMX, renvoyer uniquement le template partiel
    if request.headers.get('HX-Request'):
        return render(request, 'students/_search_results_partial.html', context)
    
    # Sinon, renvoyer la page complète
    return render(request, 'students/student_list.html', context)



def student_detail(request, pk):
    # On récupère l'étudiant ou on renvoie une erreur 404 s'il n'existe pas
    student = get_object_or_404(Student, pk=pk)
    
    # On récupère ses inscriptions (avec les infos de classe et tarif)
    # On prépare aussi l'affichage des paiements liés
    enrollments = student.enrollments.select_related('cohort', 'tariff').prefetch_related('payments').all()
    today = date.today()
    active_enrollments = enrollments.filter(is_active=True, cohort__end_date__gte=today)
    past_enrollments = enrollments.filter(Q(is_active=False) | Q(cohort__end_date__lt=today))

    current_year = AcademicYear.get_current()
    fee_paid = student.has_paid_registration_fee(current_year) if current_year else False

    context = {
        'student': student,
        'enrollments': enrollments,
        'active_enrollments': active_enrollments,
        'past_enrollments': past_enrollments,
        'current_academic_year': current_year,
        'annual_fee_paid': fee_paid,
    }
    return render(request, 'students/student_detail.html', context)


def export_student_history_csv(request, pk):
    """Exporter l'historique complet d'un étudiant en CSV"""
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related('cohort', 'tariff').prefetch_related('payments').all()

    response = HttpResponse(content_type='text/csv')
    filename = f"historique_{student.last_name}_{student.first_name}_{now().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Étudiant', 'Code', 'Cohort', 'Matière', 'Niveau', 'Professeur', 'Début', 'Fin', 'Statut', 'Tarif', 'Total Payé', 'Reste'])

    for e in enrollments:
        total_paid = sum(p.amount for p in e.payments.all())
        status = 'En cours'
        today = now().date()
        if not e.is_active:
            status = 'Résilié'
        elif e.cohort.end_date < today:
            status = 'Terminé'
        writer.writerow([
            f"{student.last_name} {student.first_name}",
            student.student_code,
            e.cohort.name,
            getattr(e.cohort.subject, 'name', ''),
            getattr(e.cohort.level, 'name', ''),
            e.cohort.teacher.get_full_name() if e.cohort.teacher else '',
            e.cohort.start_date.strftime('%d/%m/%Y'),
            e.cohort.end_date.strftime('%d/%m/%Y'),
            status,
            e.tariff.amount,
            total_paid,
            e.balance_due,
        ])

    return response


def edit_student(request, pk):
    """Modifier les informations d'un étudiant sans créer de nouvelle inscription."""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        # Champs simples
        student.first_name = request.POST.get('first_name', student.first_name)
        student.last_name = request.POST.get('last_name', student.last_name)
        sex = request.POST.get('sex', '')
        if sex or student.sex:
            student.sex = sex or student.sex
        student.email = request.POST.get('email', student.email)
        student.phone = request.POST.get('phone', student.phone)
        student.phone_2 = request.POST.get('phone_2', student.phone_2)
        student.birth_date = request.POST.get('birth_date') or None
        student.motivation = request.POST.get('motivation', student.motivation)

        # Fichiers optionnels (remplacent uniquement si fournis)
        profile_picture = request.FILES.get('profile_picture')
        id_card_front = request.FILES.get('id_card_front')
        id_card_back = request.FILES.get('id_card_back')

        if profile_picture:
            student.profile_picture = profile_picture
        if id_card_front:
            student.id_card_front = id_card_front
        if id_card_back:
            student.id_card_back = id_card_back

        student.save()
        messages.success(request, "Profil étudiant mis à jour.")

        resp = HttpResponse()
        resp['HX-Refresh'] = 'true'
        return resp

    context = {
        'student': student,
    }
    return render(request, 'students/edit_student.html', context)


def unenroll_enrollment(request, enrollment_id):
    """Résilier / désactiver une inscription sans supprimer l'historique ni les paiements."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    enrollment.is_active = False
    enrollment.save()

    messages.success(request, f"Inscription résiliée pour {enrollment.student} dans {enrollment.cohort}.")
    return redirect('students:detail', pk=enrollment.student.id)


def delete_enrollment(request, enrollment_id):
    """Supprimer définitivement une inscription et toutes les données liées (paiements, présences)."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    student_id = enrollment.student.id
    cohort_name = str(enrollment.cohort)
    enrollment.delete()  # cascade sur paiements/attendances

    messages.success(request, f"Inscription supprimée pour l'étudiant (cohort: {cohort_name}).")
    return redirect('students:detail', pk=student_id)


@require_http_methods(["POST"])
def delete_student(request, pk):
    """Supprimer un étudiant et toutes ses données (inscriptions, paiements, présences)"""
    student = get_object_or_404(Student, pk=pk)
    student_name = f"{student.first_name} {student.last_name}"
    student.delete()  # Cascade delete toutes les données liées
    return JsonResponse({'success': True, 'message': f"Étudiant {student_name} supprimé avec succès"})


@require_http_methods(["POST"])
def toggle_annual_fee(request, pk):
    """Basculer le statut de paiement des frais d'inscription annuels"""
    student = get_object_or_404(Student, pk=pk)
    current_year = AcademicYear.get_current()
    
    if not current_year:
        return JsonResponse({'success': False, 'error': 'Aucune année académique active'}, status=400)
    
    # Récupérer ou créer la fiche de frais
    fee, created = StudentAnnualFee.objects.get_or_create(
        student=student,
        academic_year=current_year,
        defaults={'amount': 1000, 'is_paid': False}
    )
    
    # Basculer le statut
    fee.is_paid = not fee.is_paid
    if fee.is_paid:
        from django.utils import timezone
        fee.paid_at = timezone.now()
    else:
        fee.paid_at = None
    fee.save()
    
    return JsonResponse({
        'success': True,
        'is_paid': fee.is_paid,
        'message': f"Frais {current_year.label} marqués comme {'payés' if fee.is_paid else 'non payés'}"
    })