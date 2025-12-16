from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from students.models import Enrollment, Attendance
from .models import Cohort, CourseSession
from datetime import datetime, date, timedelta


def cohort_list(request):
    """
    Liste de tous les groupes (cohortes) avec filtres.
    """
    cohorts = Cohort.objects.select_related(
        'subject', 'level', 'teacher', 'academic_year'
    ).prefetch_related('enrollments').all().order_by('-start_date')

    # Filtre optionnel par année académique
    year_filter = request.GET.get('year', '')
    if year_filter:
        cohorts = cohorts.filter(academic_year__id=year_filter)

    context = {
        'cohorts': cohorts,
    }
    return render(request, 'academics/cohort_list.html', context)


def cohort_detail(request, pk):
    """
    Page de détail d'un groupe avec le calendrier complet des séances.
    """
    cohort = get_object_or_404(Cohort, pk=pk)

    # Récupérer toutes les séances du groupe
    sessions = cohort.sessions.select_related('teacher', 'classroom').order_by('date', 'start_time')

    # Récupérer les inscriptions actives
    enrollments = cohort.enrollments.filter(is_active=True).select_related('student')

    # Statistiques rapides
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(status='COMPLETED').count()
    upcoming_sessions = sessions.filter(date__gte=date.today(), status='SCHEDULED').count()

    context = {
        'cohort': cohort,
        'sessions': sessions,
        'enrollments': enrollments,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'academics/cohort_detail.html', context)


def generate_sessions(request, pk):
    """
    Vue HTMX pour déclencher la génération automatique des séances.
    Met à jour le flag schedule_generated=True, ce qui déclenche le Signal.
    """
    if request.method == 'POST':
        cohort = get_object_or_404(Cohort, pk=pk)

        # Vérifier si le planning n'a pas déjà été généré
        if cohort.schedule_generated:
            return HttpResponse(
                "<div class='text-red-600 font-bold'>Le planning a déjà été généré.</div>"
            )

        # Déclencher la génération (via Signal)
        cohort.schedule_generated = True
        cohort.save()

        messages.success(request, f"Planning généré avec succès pour {cohort.name}!")

        # Rediriger vers la page de détail
        return redirect('academics:detail', pk=cohort.id)

    return HttpResponse(status=405)  # Method Not Allowed


def session_detail(request, session_id):
    """
    Page de gestion de la présence (Faire l'appel).
    GET : Affiche le formulaire avec les présences actuelles
    POST : Enregistre les statuts de présence + note de séance
    """
    session = get_object_or_404(
        CourseSession.objects.select_related('cohort', 'teacher', 'classroom'),
        id=session_id
    )

    # Récupérer toutes les inscriptions actives du groupe
    enrollments = session.cohort.enrollments.filter(is_active=True).select_related('student')

    # Récupérer les présences existantes pour cette séance
    attendances = Attendance.objects.filter(session=session).select_related('student')

    # Créer un dictionnaire {student_id: status} pour pré-remplir le formulaire
    attendance_dict = {att.student.id: att.status for att in attendances}

    # Calcul de la rémunération du prof
    duration = datetime.combine(date.today(), session.end_time) - datetime.combine(date.today(), session.start_time)
    duration_hours = duration.total_seconds() / 3600
    teacher_pay = float(duration_hours) * float(session.cohort.teacher_hourly_rate)

    if request.method == 'POST':
        # Traitement du formulaire
        try:
            # 1. Enregistrer la note de séance
            session_note = request.POST.get('session_note', '')
            session.note = session_note

            # 2. Marquer la séance comme COMPLETED
            session.status = 'COMPLETED'
            session.save()

            # 3. Mettre à jour les présences
            for enrollment in enrollments:
                student_id = enrollment.student.id
                status_key = f"status_{student_id}"
                new_status = request.POST.get(status_key, 'PRESENT')

                # Mettre à jour ou créer l'Attendance
                Attendance.objects.update_or_create(
                    session=session,
                    student=enrollment.student,
                    enrollment=enrollment,
                    defaults={'status': new_status}
                )

            messages.success(request, f"Séance validée avec succès !")
            return redirect('academics:detail', pk=session.cohort.id)

        except Exception as e:
            messages.error(request, f"Erreur lors de la validation : {str(e)}")

    context = {
        'session': session,
        'enrollments': enrollments,
        'attendance_dict': attendance_dict,
        'teacher_pay': teacher_pay,
        'duration_hours': round(duration_hours, 2),
    }
    return render(request, 'academics/session_detail.html', context)
