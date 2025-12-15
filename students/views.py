# students/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Student, Enrollment
from academics.models import Cohort
from finance.models import Discount # On importe Discount au lieu de Tariff
from django.contrib import messages

def create_enrollment(request):
    if request.method == 'GET':
        context = {
            # On ne montre que les groupes prêts et on pourra afficher leur prix standard
            'cohorts': Cohort.objects.filter(schedule_generated=True), 
            'discounts': Discount.objects.filter(is_active=True) 
        }
        return render(request, 'students/enrollment_form.html', context)
    
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone')
            
            # 1. Mise à jour ou Création de l'élève (Avec Motivation & Email)
            student, created = Student.objects.update_or_create(
                phone=phone,
                defaults={
                    'first_name': request.POST.get('first_name'),
                    'last_name': request.POST.get('last_name'),
                    'email': request.POST.get('email'),
                    'phone_2': request.POST.get('phone_2', ''),
                    'motivation': request.POST.get('motivation', ''),
                    # Code étudiant généré basiquement si pas existant
                    'student_code': f"ST-{phone[-4:]}" 
                }
            )

            # 2. Gestion du Discount (peut être vide/None)
            discount_id = request.POST.get('discount_id')
            discount_obj = None
            if discount_id:
                discount_obj = Discount.objects.get(id=discount_id)

            # 3. Création de l'inscription
            # Le calcul du prix final (agreed_amount) se fera automatiquement dans le .save() du modèle
            Enrollment.objects.create(
                student=student,
                cohort_id=request.POST.get('cohort_id'),
                discount=discount_obj, # Passe l'objet ou None
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
from django.db.models import Q
from .models import Student
from academics.models import Cohort

def student_list(request):
    # 1. Récupération des paramètres GET (ce qu'il y a dans l'URL ?q=yanis&cohort=1)
    search_query = request.GET.get('q', '')
    cohort_filter = request.GET.get('cohort', '')

    # 2. Requête de base optimisée
    students = Student.objects.prefetch_related('enrollments__cohort', 'enrollments__tariff').all().order_by('-created_at')

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

    context = {
        'students': page_obj, # On passe la page, pas toute la liste
        'search_query': search_query,
        'cohort_filter': int(cohort_filter) if cohort_filter else '',
        'all_cohorts': all_cohorts,
    }
    return render(request, 'students/student_list.html', context)



def student_detail(request, pk):
    # On récupère l'étudiant ou on renvoie une erreur 404 s'il n'existe pas
    student = get_object_or_404(Student, pk=pk)
    
    # On récupère ses inscriptions (avec les infos de classe et tarif)
    # On prépare aussi l'affichage des paiements liés
    enrollments = student.enrollments.select_related('cohort', 'tariff').prefetch_related('payments').all()
    
    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'students/student_detail.html', context)