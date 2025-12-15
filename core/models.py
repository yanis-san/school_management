from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Utilisateur système (Admin, Staff, Professeur)"""
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

class AcademicYear(models.Model):
    """Ex: 2024-2025"""
    label = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self): return self.label

class Classroom(models.Model):
    name = models.CharField(max_length=50) # Ex: Salle Tokyo
    capacity = models.IntegerField(default=15)
    
    def __str__(self): return self.name