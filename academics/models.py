# academics/models.py
from django.db import models
from core.models import User, Classroom, AcademicYear
from datetime import timedelta, date

class Subject(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Level(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class Cohort(models.Model):
    """
    Le Groupe (La Classe).
    """
    name = models.CharField(max_length=150)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    
    # Période globale
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='cohorts')
    start_date = models.DateField()
    end_date = models.DateField()

    # --- ENSEIGNANTS & PAIE ---
    # Prof Titulaire
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'is_teacher': True}, related_name='assigned_cohorts')
    
    # Prof Suppléant (C'est ce champ qui manquait !)
    substitute_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'is_teacher': True}, 
        related_name='substitute_cohorts', 
        verbose_name="Professeur Suppléant"
    )

    # Tarif Horaire (Pour la paie)
    teacher_hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Tarif Horaire Prof (DA/h)",
        help_text="Tarif appliqué pour chaque heure de cours de ce groupe"
    )


    # NOUVEAU : Le prix standard pour TOUT LE MONDE dans ce groupe
    standard_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Prix Standard (DA)"
    )

    # Flag pour déclencher la génération automatique via Signal
    schedule_generated = models.BooleanField(default=False, help_text="Cochez pour générer les séances")

    def __str__(self): return self.name

class WeeklySchedule(models.Model):
    """Le 'Patron' (Template) Hebdomadaire."""
    DAYS = [
        (0, 'Lundi'), (1, 'Mardi'), (2, 'Mercredi'), (3, 'Jeudi'), 
        (4, 'Vendredi'), (5, 'Samedi'), (6, 'Dimanche')
    ]
    cohort = models.ForeignKey(Cohort, related_name='weekly_schedules', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT)

class CourseSession(models.Model):
    """La Séance Réelle."""
    STATUS_CHOICES = [
        ('SCHEDULED', 'Prévu'),
        ('COMPLETED', 'Réalisé'),
        ('CANCELLED', 'Annulé'),   # Ne compte pas, pas de rattrapage
        ('POSTPONED', 'Reporté'),  # Doit générer un rattrapage
    ]

    cohort = models.ForeignKey(Cohort, related_name='sessions', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # On peut changer le prof ou la salle juste pour CETTE séance
    teacher = models.ForeignKey(User, on_delete=models.PROTECT)
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.cohort} - {self.date} ({self.get_status_display()})"