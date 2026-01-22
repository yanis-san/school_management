#!/usr/bin/env python
"""
Script de test pour vérifier que les abréviations se créent automatiquement
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from academics.models import Cohort, Subject, Level
from core.models import User
from datetime import date

print("=" * 80)
print("TEST AUTOMATIQUE DES ABRÉVIATIONS")
print("=" * 80)

# Récupérer ou créer les données de test
subject = Subject.objects.get_or_create(name='Français')[0]
level = Level.objects.get_or_create(name='Niveau 2')[0]
teacher = User.objects.filter(is_teacher=True).first()

if teacher:
    # Test 1: Créer un nouveau cohort
    print("\n1️⃣ TEST: Création d'un nouveau cohort")
    print("-" * 80)
    
    cohort = Cohort(
        subject=subject,
        level=level,
        teacher=teacher,
        start_date=date(2026, 2, 1),  # Février pour éviter les collisions
        end_date=date(2026, 4, 30),
        modality='IN_PERSON',
        is_individual=False
    )
    cohort.save()
    
    print(f"✅ Nouveau cohort créé !")
    print(f"   Nom: {cohort.name}")
    print(f"   Abréviation en base: {cohort.abbreviation}")
    print(f"   get_abbreviation(): {cohort.get_abbreviation()}")
    
    # Vérifier la cohérence
    if cohort.abbreviation == 'FRA2P0226':
        print("   ✅ Abréviation correcte !")
    else:
        print(f"   ❌ Abréviation incorrect. Attendu: FRA2P0226, Obtenu: {cohort.abbreviation}")
    
    # Test 2: Modifier le cohort
    print("\n2️⃣ TEST: Modification du cohort")
    print("-" * 80)
    
    original_abbr = cohort.abbreviation
    cohort.start_date = date(2026, 6, 1)  # Juin au lieu de février
    cohort.save()
    
    print(f"   Ancienne abréviation: {original_abbr}")
    print(f"   Nouvelle date: {cohort.start_date}")
    print(f"   Nouvelle abréviation: {cohort.abbreviation}")
    
    if cohort.abbreviation == 'FRA2P0626':
        print("   ✅ Abréviation mise à jour correctement !")
    else:
        print(f"   ❌ Abréviation incorrect. Attendu: FRA2P0626, Obtenu: {cohort.abbreviation}")
    
    # Test 3: Afficher les cohorts existants
    print("\n3️⃣ RÉSUMÉ: Tous les cohorts avec abréviations")
    print("-" * 80)
    
    cohorts = Cohort.objects.all().order_by('-id')[:10]
    print(f"\n{'ID':>3} | {'Nom':<45} | {'Abréviation':<12}")
    print("-" * 80)
    for c in cohorts:
        print(f"{c.id:3d} | {c.name[:45]:<45} | {c.abbreviation:<12}")
    
    # Test 4: Vérifier l'unicité
    print("\n4️⃣ TEST: Vérifier l'unicité des abréviations")
    print("-" * 80)
    
    all_abbrs = Cohort.objects.values_list('abbreviation', flat=True)
    unique_abbrs = set(all_abbrs)
    
    print(f"   Total de cohorts: {len(all_abbrs)}")
    print(f"   Abréviations uniques: {len(unique_abbrs)}")
    print(f"   Vides: {Cohort.objects.filter(abbreviation='').count()}")
    
    if len(all_abbrs) == len(unique_abbrs):
        print("   ✅ Toutes les abréviations sont uniques !")
    else:
        print(f"   ❌ Il y a {len(all_abbrs) - len(unique_abbrs)} doublons")
        
        # Afficher les doublons
        from django.db.models import Count
        dupes = Cohort.objects.values('abbreviation').annotate(count=Count('id')).filter(count__gt=1)
        for dupe in dupes:
            print(f"      - {dupe['abbreviation']}: {dupe['count']} fois")
    
    print("\n" + "=" * 80)
    print("✅ TESTS TERMINÉS")
    print("=" * 80)

else:
    print("❌ Aucun professeur trouvé")
