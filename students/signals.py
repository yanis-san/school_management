from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Enrollment, Attendance
from academics.models import CourseSession

# --- AUTOMATISME 1 : Inscription -> Génération Présence Future ---
@receiver(post_save, sender=Enrollment)
def create_attendance_for_new_enrollment(sender, instance, created, **kwargs):
    """
    Quand un élève s'inscrit, on l'ajoute automatiquement 
    à toutes les séances FUTURES du groupe.
    """
    if created and instance.is_active:
        # Récupérer les séances à venir
        future_sessions = CourseSession.objects.filter(
            cohort=instance.cohort,
            date__gte=timezone.now().date()
        )
        
        attendances = []
        for session in future_sessions:
            # On vérifie pour éviter les doublons
            if not Attendance.objects.filter(session=session, student=instance.student).exists():
                attendances.append(Attendance(
                    session=session,
                    student=instance.student,
                    enrollment=instance,
                    status='PRESENT', # On présume qu'il sera là
                    billable=True     # Par défaut, c'est facturable
                ))
        
        if attendances:
            Attendance.objects.bulk_create(attendances)

# --- AUTOMATISME 2 : Nouvelle Séance -> Ajout des Élèves Inscrits ---
@receiver(post_save, sender=CourseSession)
def create_attendance_for_new_session(sender, instance, created, **kwargs):
    """
    Quand une séance est créée (ou reportée/générée), 
    on crée les lignes de présence pour tous les élèves ACTIFS.
    """
    if created:
        active_enrollments = Enrollment.objects.filter(
            cohort=instance.cohort,
            is_active=True
        )
        
        attendances = []
        for enrollment in active_enrollments:
            attendances.append(Attendance(
                session=instance,
                student=enrollment.student,
                enrollment=enrollment,
                status='PRESENT',
                billable=True
            ))
        
        if attendances:
            Attendance.objects.bulk_create(attendances)

# --- AUTOMATISME 3 : Modification Présence -> Recalcul Heures Consommées ---
@receiver(post_save, sender=Attendance)
def recalculate_hours_consumed(sender, instance, **kwargs):
    """
    Recalcule les heures consommées basé sur le champ 'billable'.
    Permet de facturer une absence non excusée ou d'offrir une séance.
    """
    enrollment = instance.enrollment
    
    # Si ce n'est pas un pack d'heures, on s'en fiche
    if enrollment.payment_plan != 'PACK':
        return

    # ON PREND TOUT CE QUI EST "FACTURABLE" (billable=True)
    # Peu importe si le statut est 'PRESENT', 'ABSENT' ou 'LATE'
    charged_attendances = Attendance.objects.filter(
        enrollment=enrollment,
        billable=True 
    ).select_related('session')
    
    total_hours = 0
    for att in charged_attendances:
        # Calcul durée séance
        start = att.session.start_time
        end = att.session.end_time
        
        # Durée en heures décimales
        duration = (end.hour + end.minute/60.0) - (start.hour + start.minute/60.0)
        total_hours += duration
    
    # Mise à jour directe du champ sur l'inscription
    enrollment.hours_consumed = total_hours
    enrollment.save(update_fields=['hours_consumed'])