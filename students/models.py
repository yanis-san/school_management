# students/models.py
from django.db import models
from core.models import User
from academics.models import Cohort
from finance.models import Tariff

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    phone_2 = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True, null=True)
    motivation = models.TextField(blank=True, verbose_name="Pourquoi ?")
    # Code étudiant unique (généré auto ou manuel)
    student_code = models.CharField(max_length=20, unique=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/students/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name.upper()} {self.first_name}"

    @property
    def age(self):
        """Calcule l'âge à partir de la date de naissance"""
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

class Enrollment(models.Model):
    """
    LE CONTRAT.
    Lie un étudiant à un groupe, fixe le prix et le mode de paiement.
    """
    PAYMENT_PLANS = [
        ('FULL', 'Totalité (Une fois)'),
        ('MONTHLY', 'Mensuel (Échéancier)'),
        ('PACK', 'Pack d\'Heures (Débit à la séance)'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, related_name='enrollments')
    
    # Financier
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT, verbose_name="Tarif Appliqué")
    payment_plan = models.CharField(max_length=10, choices=PAYMENT_PLANS, default='FULL')
    
    # Crédits d'heures (Pour le mode PACK/Individuel)
    hours_purchased = models.DecimalField(default=0, max_digits=5, decimal_places=1, help_text="Si Pack d'heures")
    hours_consumed = models.DecimalField(default=0, max_digits=5, decimal_places=1)

    is_active = models.BooleanField(default=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} -> {self.cohort} ({self.get_payment_plan_display()})"
    
    @property
    def balance_due(self):
        """Calcul dynamique du reste à payer total"""
        total_paid = sum(p.amount for p in self.payments.all())
        return self.tariff.amount - total_paid
    


class Attendance(models.Model):
    """
    La ligne de présence individuelle.
    """
    STATUS_CHOICES = [
        ('PRESENT', 'Présent'),
        ('ABSENT', 'Absent'),
        ('LATE', 'En Retard'),
        ('EXCUSED', 'Excusé'),
    ]

    session = models.ForeignKey('academics.CourseSession', on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    
    # --- NOUVEAU CHAMP ---
    # Par défaut True : une séance prévue est due, sauf si l'admin décide le contraire.
    billable = models.BooleanField(default=True, verbose_name="Facturable (Déduire du pack)")
    
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        etat = "Facturé" if self.billable else "Offert/Excusé"
        return f"{self.student} - {self.session} ({self.status} - {etat})"