from django.db import models
from django.utils import timezone


class Prospect(models.Model):
    """Prospects venant du formulaire de contact du site"""
    
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Âge")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    level = models.CharField(max_length=50, blank=True, verbose_name="Niveau")
    source = models.CharField(max_length=100, blank=True, verbose_name="Source")
    activity_type = models.CharField(max_length=200, blank=True, verbose_name="Type d'activité")
    specific_course = models.CharField(max_length=200, blank=True, verbose_name="Cours spécifique")
    message = models.TextField(blank=True, verbose_name="Message")
    notes = models.TextField(blank=True, verbose_name="Notes")
    converted = models.BooleanField(default=False, verbose_name="Converti")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Prospect"
        verbose_name_plural = "Prospects"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_activity_summary(self):
        """Retourne un résumé des intérêts"""
        parts = []
        if self.activity_type:
            parts.append(self.activity_type)
        if self.specific_course:
            parts.append(self.specific_course)
        return " - ".join(parts) if parts else "Non spécifié"
