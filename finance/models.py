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