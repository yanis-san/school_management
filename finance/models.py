# finance/models.py
from django.db import models
from core.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Tariff(models.Model):
    """
    Le Catalogue des Prix.
    On ne saisit pas le prix à la main à chaque élève. On choisit un tarif.
    Ex: "Tarif 2025 - Japonais N1 - Standard" = 30 000 DA
    Ex: "Tarif 2025 - Japonais N1 - Ancien Élève" = 25 000 DA
    """
    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant Total")
    
    # Optionnel : Lier ce tarif à un type de cours spécifique pour filtrer les listes
    # linked_course_type = models.ForeignKey(...) 

    def __str__(self):
        return f"{self.name} ({self.amount} DA)"

class Payment(models.Model):
    """
    L'argent qui rentre réellement dans la caisse.
    """
    METHODS = [
        ('CASH', 'Espèces'),
        ('CARD', 'Virement/Carte'),
        ('CHECK', 'Chèque'),
    ]

    # On utilise une chaîne de caractères ('students.Enrollment') pour éviter les imports circulaires
    enrollment = models.ForeignKey('students.Enrollment', on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHODS, default='CASH')
    date = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Numéro de chèque ou virement")
    
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.amount} DA - {self.enrollment}"

class Installment(models.Model):
    """
    Les Échéances (Ce que l'élève DOIT payer et QUAND).
    Généré automatiquement selon le plan de paiement choisi.
    """
    enrollment = models.ForeignKey('students.Enrollment', on_delete=models.CASCADE, related_name='installments')
    due_date = models.DateField(verbose_name="Date d'échéance")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant dû")
    
    is_paid = models.BooleanField(default=False)
    
    # Lien vers le paiement qui a soldé cette échéance (optionnel, pour traçabilité)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='covered_installments')

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        status = "PAYÉ" if self.is_paid else "IMPAYÉ"
        return f"{self.due_date} : {self.amount} DA ({status})"
    


class Discount(models.Model):
    """
    Gestion des promotions (individuelles ou groupe).
    Ex: "Réduction Fratrie (-10%)" ou "Bourse (-5000 DA)"
    """
    TYPES = [
        ('PERCENT', 'Pourcentage (%)'),
        ('FIXED', 'Montant Fixe (DA)'),
    ]

    name = models.CharField(max_length=100) # Ex: Promo Ouverture
    value = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPES, default='FIXED')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        symbole = "%" if self.type == 'PERCENT' else "DA"
        return f"{self.name} (-{self.value} {symbole})"


class TeacherPayment(models.Model):
    """
    Historique des paiements aux professeurs (Sorties d'argent).
    Enregistre chaque versement de salaire avec la période couverte.
    """
    PAYMENT_METHODS = [
        ('CASH', 'Espèces'),
        ('TRANSFER', 'Virement (CCP/RIB)'),
        ('CHECK', 'Chèque'),
    ]

    # Professeur concerné
    teacher = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={'is_teacher': True},
        related_name='salary_payments',
        verbose_name="Professeur"
    )

    # Période couverte par ce paiement
    period_start = models.DateField(verbose_name="Début de Période")
    period_end = models.DateField(verbose_name="Fin de Période")

    # Montant et méthode
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant Total Payé (DA)"
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        verbose_name="Méthode de Paiement"
    )

    # Métadonnées
    payment_date = models.DateField(
        verbose_name="Date de Paiement",
        help_text="Date à laquelle le paiement a été effectué"
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='teacher_payments_recorded',
        verbose_name="Enregistré par"
    )

    # Justificatifs et notes
    proof_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Référence",
        help_text="N° de chèque, référence virement, etc."
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Informations complémentaires sur ce paiement"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Paiement Professeur"
        verbose_name_plural = "Paiements Professeurs"

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.total_amount} DA ({self.payment_date})"