#!/usr/bin/env python
"""Test génération des noms de cohort selon modalité et format"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from academics.models import Cohort, Subject, Level
from core.models import AcademicYear
from datetime import date

# Test les différentes combinaisons de noms
year = AcademicYear.objects.first()
subject = Subject.objects.first()
level = Level.objects.first()

if year and subject and level:
    print("\n" + "="*70)
    print("TEST: Génération des noms de cohort")
    print("="*70 + "\n")
    
    test_cases = [
        (False, 'IN_PERSON', 'Groupe - Présentiel'),
        (False, 'ONLINE', 'Groupe - En ligne'),
        (True, 'IN_PERSON', 'Individuel - Présentiel'),
        (True, 'ONLINE', 'Individuel - En ligne'),
    ]
    
    for is_indiv, modality, description in test_cases:
        c = Cohort(
            subject=subject,
            level=level,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 12, 30),
            academic_year=year,
            is_individual=is_indiv,
            modality=modality
        )
        name = c.generate_name()
        print(f"✓ {description:30} → {name}")
    
    print("\n" + "="*70 + "\n")
