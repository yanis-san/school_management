from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from students.models import Enrollment, Attendance
from .models import Cohort, CourseSession
from datetime import datetime, date, timedelta
from django.db.models import Count, Q
from core.models import AcademicYear


def cohort_list(request):
    """
    Liste de tous les groupes (cohortes) avec filtres.
    """
    cohorts = Cohort.objects.select_related(
        'subject', 'level', 'teacher', 'academic_year'
    ).prefetch_related('enrollments').annotate(
        remaining=Count('sessions', filter=Q(sessions__status__in=['SCHEDULED', 'POSTPONED']))
    ).all().order_by('-start_date')

    # Filtres
    year_filter = request.GET.get('year', '')  # id de l'année académique
    if year_filter:
        cohorts = cohorts.filter(academic_year__id=year_filter)

    status_filter = request.GET.get('status', '')  # 'finished' | 'ongoing'
    if status_filter == 'finished':
        cohorts = cohorts.filter(remaining=0)
    elif status_filter == 'ongoing':
        cohorts = cohorts.filter(remaining__gt=0)

    modality_filter = request.GET.get('modality', '')  # 'ONLINE' | 'IN_PERSON'
    if modality_filter in ['ONLINE', 'IN_PERSON']:
        cohorts = cohorts.filter(modality=modality_filter)

    individual_filter = request.GET.get('individual', '')  # '1' | '0'
    if individual_filter == '1':
        cohorts = cohorts.filter(is_individual=True)
    elif individual_filter == '0':
        cohorts = cohorts.filter(is_individual=False)

    years = AcademicYear.objects.all().order_by('-start_date')

    context = {
        'cohorts': cohorts,
        'status_filter': status_filter,
        'year_filter': year_filter,
        'modality_filter': modality_filter,
        'individual_filter': individual_filter,
        'years': years,
    }
    return render(request, 'academics/cohort_list.html', context)


def cohort_detail(request, pk):
    """
    Page de détail d'un groupe avec le calendrier complet des séances.
    """
    cohort = get_object_or_404(Cohort, pk=pk)

    # Formulaire léger pour configurer le mode Ramadan sans passer par l'admin
    if request.method == 'POST':
        try:
            rs = (request.POST.get('ramadan_start') or '').strip()
            re = (request.POST.get('ramadan_end') or '').strip()
            rst = (request.POST.get('ramadan_start_time') or '').strip()
            ret = (request.POST.get('ramadan_end_time') or '').strip()
            rrate = (request.POST.get('ramadan_teacher_hourly_rate') or '').strip()

            cohort.ramadan_start = datetime.strptime(rs, '%Y-%m-%d').date() if rs else None
            cohort.ramadan_end = datetime.strptime(re, '%Y-%m-%d').date() if re else None
            cohort.ramadan_start_time = datetime.strptime(rst, '%H:%M').time() if rst else None
            cohort.ramadan_end_time = datetime.strptime(ret, '%H:%M').time() if ret else None
            cohort.ramadan_teacher_hourly_rate = int(rrate) if rrate else None

            cohort.save(update_fields=[
                'ramadan_start', 'ramadan_end', 'ramadan_start_time', 'ramadan_end_time',
                'ramadan_teacher_hourly_rate'
            ])
            messages.success(request, "Paramètres Ramadan enregistrés pour ce groupe.")
            return redirect('academics:detail', pk=cohort.id)
        except ValueError:
            messages.error(request, "Valeurs invalides pour les dates/heures Ramadan.")
            return redirect('academics:detail', pk=cohort.id)

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
        'today': date.today(),
    }
    return render(request, 'academics/cohort_detail.html', context)


def generate_sessions(request, pk):
    """
    Vue HTMX pour déclencher la génération automatique des séances.
    Met à jour le flag schedule_generated=True, ce qui déclenche le Signal.
    """
    if request.method == 'POST':
        cohort = get_object_or_404(Cohort, pk=pk)
        # 1) Vérifier qu'il y a bien des créneaux hebdomadaires
        schedules = cohort.weekly_schedules.all()
        if not schedules.exists():
            return HttpResponse(
                "<div class='text-red-600 font-bold'>Aucun créneau hebdomadaire (WeeklySchedule) n'est défini pour ce groupe. Créez-en d'abord dans l'admin.</div>"
            )

        # 2) Si déjà généré ET qu'il y a des séances, on empêche le doublon
        if cohort.schedule_generated and cohort.sessions.exists():
            return HttpResponse(
                "<div class='text-red-600 font-bold'>Le planning a déjà été généré.</div>"
            )

        # 3) Génération manuelle (idem signal) pour garantir la création
        if not cohort.sessions.exists():
            current_date = cohort.start_date
            sessions_to_create = []

            while current_date <= cohort.end_date:
                weekday = current_date.weekday()  # 0 = Lundi
                for sched in schedules:
                    if sched.day_of_week == weekday:
                        sessions_to_create.append(
                            CourseSession(
                                cohort=cohort,
                                date=current_date,
                                start_time=sched.start_time,
                                end_time=sched.end_time,
                                teacher=cohort.teacher,
                                classroom=sched.classroom,
                                status='SCHEDULED'
                            )
                        )
                current_date += timedelta(days=1)

            CourseSession.objects.bulk_create(sessions_to_create)

        # 4) Marquer comme généré (le signal ne recréera pas car des séances existent déjà)
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

    # Calcul de la rémunération du prof (utilise override si présent)
    duration_hours = float(session.duration_hours)
    teacher_pay = float(duration_hours) * float(session.cohort.teacher_hourly_rate)
    
    # Calculer heures et minutes pour le formulaire
    override_h = 0
    override_m = 0
    if session.duration_override_minutes:
        override_h = session.duration_override_minutes // 60
        override_m = session.duration_override_minutes % 60

    # Mode édition si demandé explicitement en GET (?edit=1)
    is_editing = request.GET.get('edit') == '1'

    if request.method == 'POST':
        # Verrou: si le groupe est terminé, on bloque toute modification
        if session.cohort.is_finished:
            messages.error(request, "Groupe terminé : modifications verrouillées.")
            return redirect('academics:detail', pk=session.cohort.id)
        
        # 0. Gérer le choix du professeur (nouveau)
        teacher_id = request.POST.get('teacher_id', '')
        if teacher_id:
            try:
                new_teacher = User.objects.get(id=int(teacher_id), is_teacher=True)
                # Vérifier que c'est le titulaire ou un des remplaçants
                if new_teacher == session.cohort.teacher or new_teacher in session.cohort.substitute_teachers.all():
                    session.teacher = new_teacher
                    messages.info(request, f"Professeur changé à {new_teacher.get_full_name()}")
                else:
                    messages.error(request, "Ce professeur n'est pas autorisé pour ce groupe.")
            except (User.DoesNotExist, ValueError):
                messages.error(request, "Professeur invalide.")
        
        # Traitement du formulaire (reste inchangé)
        try:
            # 1. Gérer une éventuelle surcharge de durée (facultatif)
            clear_override = request.POST.get('clear_override') == '1'
            override_h = request.POST.get('override_hours', '').strip()
            override_m = request.POST.get('override_minutes', '').strip()

            if clear_override:
                session.duration_override_minutes = None
            else:
                if override_h or override_m:
                    oh = int(override_h) if override_h and override_h.isdigit() else 0
                    om = int(override_m) if override_m and override_m.isdigit() else 0
                    total_minutes = max(0, oh * 60 + om)
                    if total_minutes > 0:
                        session.duration_override_minutes = total_minutes
                        messages.info(request, f"Override enregistré: {total_minutes} min ({total_minutes/60:.1f}h)")
                    else:
                        session.duration_override_minutes = None

            # 2. Enregistrer la note de séance
            session_note = request.POST.get('session_note', '')
            session.note = session_note

            # 3. Marquer la séance comme COMPLETED
            session.status = 'COMPLETED'
            session.save()

            # 4. Mettre à jour les présences (PRESENT/ABSENT uniquement)
            for enrollment in enrollments:
                student_id = enrollment.student.id
                status_key = f"status_{student_id}"
                new_status = request.POST.get(status_key, 'PRESENT')
                if new_status not in ['PRESENT', 'ABSENT']:
                    new_status = 'PRESENT'

                # Mettre à jour ou créer l'Attendance
                # On match uniquement sur session et student (contrainte unique)
                Attendance.objects.update_or_create(
                    session=session,
                    student=enrollment.student,
                    defaults={
                        'status': new_status,
                        'enrollment': enrollment
                    }
                )

            messages.success(request, f"Séance validée avec succès !")
            # Après validation, on revient à la page du groupe.
            return redirect('academics:detail', pk=session.cohort.id)

        except Exception as e:
            messages.error(request, f"Erreur lors de la validation : {str(e)}")

    context = {
        'session': session,
        'enrollments': enrollments,
        'attendance_dict': attendance_dict,
        'teacher_pay': teacher_pay,
        'duration_hours': round(duration_hours, 2),
        'override_h': override_h,
        'override_m': override_m,
        'is_editing': is_editing,
        'available_teachers': [session.cohort.teacher] + list(session.cohort.substitute_teachers.all()),
    }
    return render(request, 'academics/session_detail.html', context)


def postpone_session(request, session_id):
    """
    Marque une séance comme reportée (POSTPONED).
    Le signal handle_session_changes créera automatiquement un rattrapage.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    session = get_object_or_404(CourseSession, id=session_id)

    # Si déjà annulée ou reportée, on évite les doublons
    if session.status in ['POSTPONED', 'CANCELLED']:
        messages.info(request, "Cette séance est déjà reportée ou annulée.")
        return redirect('academics:detail', pk=session.cohort.id)

    session.status = 'POSTPONED'
    session.note = (session.note or '') + "\n[Auto] Séance reportée via bouton." if session.note else "[Auto] Séance reportée via bouton."
    session.save()

    messages.success(request, "Séance marquée comme reportée. Un rattrapage sera ajouté automatiquement.")
    return redirect('academics:detail', pk=session.cohort.id)


def cancel_postpone(request, session_id):
    """
    Annule le report d'une séance : remet en SCHEDULED et supprime le rattrapage créé.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    session = get_object_or_404(CourseSession, id=session_id)

    if session.status != 'POSTPONED':
        messages.warning(request, "Cette séance n'est pas reportée.")
        return redirect('academics:detail', pk=session.cohort.id)

    # Remettre en Prévu
    session.status = 'SCHEDULED'
    # Nettoyer la note automatique
    if "[Auto] Séance reportée via bouton." in (session.note or ''):
        session.note = session.note.replace("[Auto] Séance reportée via bouton.", "").strip()
    session.save()

    # Supprimer le rattrapage créé (identifié par la note contenant la date de cette séance)
    makeup_session = CourseSession.objects.filter(
        cohort=session.cohort,
        note__contains=f"Rattrapage séance du {session.date}"
    ).first()

    if makeup_session:
        makeup_session.delete()
        messages.success(request, "Report annulé. La séance est remise en 'Prévu' et le rattrapage supprimé.")
    else:
        messages.info(request, "Report annulé. Aucune séance de rattrapage automatique trouvée à supprimer.")

    return redirect('academics:detail', pk=session.cohort.id)


def change_session_teacher(request, session_id):
    """
    Permet de changer le professeur d'une séance spécifique.
    GET : Affiche le formulaire avec la liste des profs actifs
    POST : Enregistre le nouveau prof et note le changement
    """
    from core.models import User
    
    session = get_object_or_404(
        CourseSession.objects.select_related('cohort', 'teacher', 'classroom'),
        id=session_id
    )
    
    # Liste de tous les professeurs actifs
    all_teachers = User.objects.filter(is_teacher=True, is_active=True).order_by('first_name', 'last_name')
    
    if request.method == 'POST':
        new_teacher_id = request.POST.get('teacher_id')
        if not new_teacher_id:
            messages.error(request, "Veuillez sélectionner un professeur.")
            return redirect('academics:change_session_teacher', session_id=session_id)
        
        new_teacher = get_object_or_404(User, id=new_teacher_id, is_teacher=True)
        old_teacher = session.teacher
        
        # Mettre à jour le professeur
        session.teacher = new_teacher
        
        # Ajouter une note pour traçabilité
        change_note = f"\n[Changement prof: {old_teacher.get_full_name()} → {new_teacher.get_full_name()}]"
        session.note = (session.note or '') + change_note
        session.save()
        
        messages.success(
            request, 
            f"Professeur changé avec succès. Cette séance sera payée à {new_teacher.get_full_name()}."
        )
        return redirect('academics:detail', pk=session.cohort.id)
    
    context = {
        'session': session,
        'all_teachers': all_teachers,
        'cohort_teacher': session.cohort.teacher,
        'substitute_teacher': session.cohort.substitute_teacher,
    }
    return render(request, 'academics/change_session_teacher.html', context)
