#!/usr/bin/env python
"""Vérifie si les overrides de séances sont enregistrés"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from academics.models import CourseSession

print("=" * 80)
print("VÉRIFICATION DES OVERRIDES DE SÉANCES")
print("=" * 80)

sessions = CourseSession.objects.filter(status='COMPLETED').order_by('-date')[:10]

for session in sessions:
    print(f"\n📅 {session.date} | {session.start_time} - {session.end_time}")
    print(f"   Cohort: {session.cohort.name}")
    print(f"   Prof: {session.teacher.get_full_name()}")
    
    if session.duration_override_minutes:
        print(f"   ✅ Override: {session.duration_override_minutes} min ({session.duration_hours}h)")
    else:
        print(f"   ⏱️  Durée calculée: {session.duration_hours}h (pas d'override)")
    
    pay = session.duration_hours * session.cohort.teacher_hourly_rate
    print(f"   💰 Paie: {pay} DA ({session.duration_hours}h × {session.cohort.teacher_hourly_rate} DA/h)")

print("\n" + "=" * 80)
