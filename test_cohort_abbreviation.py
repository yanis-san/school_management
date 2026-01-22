"""
Script de test pour la méthode get_abbreviation() du modèle Cohort.
Usage: python manage.py shell < test_cohort_abbreviation.py
"""

from datetime import datetime, date
from academics.models import Cohort, Subject, Level, LANGUAGE_CODES, MODALITY_CODES

print("=" * 80)
print("TEST DE LA MÉTHODE get_abbreviation()")
print("=" * 80)

# Afficher les codes disponibles
print("\n📚 CODES DE LANGUES DISPONIBLES:")
print("-" * 80)
for i, (lang, code) in enumerate(sorted(LANGUAGE_CODES.items()), 1):
    print(f"  {code:4} → {lang}")
    if i % 2 == 0:
        print()

print("\n🔄 CODES DE MODALITÉ:")
print("-" * 80)
for (modality, is_individual), code in MODALITY_CODES.items():
    modality_name = "En ligne" if modality == "ONLINE" else "Présentiel"
    type_name = "Individuel" if is_individual else "Groupe"
    print(f"  {code:2} → {modality_name:10} - {type_name}")

print("\n" + "=" * 80)
print("TESTS D'ABRÉVIATION")
print("=" * 80)

# Récupérer ou créer les données nécessaires
try:
    # Créer un Subject de test
    subject_chinois = Subject.objects.get_or_create(name='Chinois')[0]
    subject_japonais = Subject.objects.get_or_create(name='Japonais')[0]
    subject_coreen = Subject.objects.get_or_create(name='Coréen')[0]
    
    # Créer des Levels de test
    level_3 = Level.objects.get_or_create(name='Niveau 3')[0]
    level_6 = Level.objects.get_or_create(name='Niveau 6')[0]
    level_1 = Level.objects.get_or_create(name='Niveau 1')[0]
    
    print("\n✓ Données de test créées/récupérées")
    
    # Récupérer le premier prof (pour le test)
    from core.models import User
    teacher = User.objects.filter(is_teacher=True).first()
    if not teacher:
        print("⚠️  Aucun professeur trouvé pour les tests")
        exit(1)
    
    print(f"✓ Professeur trouvé: {teacher.username}\n")
    
    # Test 1: Chinois Niveau 3 - Présentiel Groupe
    print("\n📌 TEST 1: Chinois Niveau 3 (Présentiel Groupe)")
    print("-" * 80)
    cohort_1 = Cohort(
        subject=subject_chinois,
        level=level_3,
        start_date=date(2026, 1, 15),
        end_date=date(2026, 3, 15),
        teacher=teacher,
        modality='IN_PERSON',
        is_individual=False
    )
    abbr_1 = cohort_1.get_abbreviation()
    print(f"Nom complet: Chinois Niveau 3 (présentiel) - Jan 2026")
    print(f"Abréviation: {abbr_1}")
    print(f"✓ Attendu: CHN3P0126 → {'✅ CORRECT' if abbr_1 == 'CHN3P0126' else '❌ ERREUR'}")
    
    # Test 2: Japonais Niveau 6 - En ligne Groupe
    print("\n📌 TEST 2: Japonais Niveau 6 (En ligne Groupe)")
    print("-" * 80)
    cohort_2 = Cohort(
        subject=subject_japonais,
        level=level_6,
        start_date=date(2026, 1, 20),
        end_date=date(2026, 3, 20),
        teacher=teacher,
        modality='ONLINE',
        is_individual=False
    )
    abbr_2 = cohort_2.get_abbreviation()
    print(f"Nom complet: Japonais Niveau 6 (en ligne) - Jan 2026")
    print(f"Abréviation: {abbr_2}")
    print(f"✓ Attendu: JPN6O0126 → {'✅ CORRECT' if abbr_2 == 'JPN6O0126' else '❌ ERREUR'}")
    
    # Test 3: Japonais Niveau 6 - En ligne Individuel
    print("\n📌 TEST 3: Japonais Niveau 6 (En ligne Individuel)")
    print("-" * 80)
    cohort_3 = Cohort(
        subject=subject_japonais,
        level=level_6,
        start_date=date(2026, 1, 25),
        end_date=date(2026, 3, 25),
        teacher=teacher,
        modality='ONLINE',
        is_individual=True
    )
    abbr_3 = cohort_3.get_abbreviation()
    print(f"Nom complet: Japonais Niveau 6 (individuel en ligne) - Jan 2026")
    print(f"Abréviation: {abbr_3}")
    print(f"✓ Attendu: JPN6IO0126 → {'✅ CORRECT' if abbr_3 == 'JPN6IO0126' else '❌ ERREUR'}")
    
    # Test 4: Coréen Niveau 1 - Présentiel Individuel
    print("\n📌 TEST 4: Coréen Niveau 1 (Présentiel Individuel)")
    print("-" * 80)
    cohort_4 = Cohort(
        subject=subject_coreen,
        level=level_1,
        start_date=date(2026, 1, 10),
        end_date=date(2026, 3, 10),
        teacher=teacher,
        modality='IN_PERSON',
        is_individual=True
    )
    abbr_4 = cohort_4.get_abbreviation()
    print(f"Nom complet: Coréen Niveau 1 (individuel présentiel) - Jan 2026")
    print(f"Abréviation: {abbr_4}")
    print(f"✓ Attendu: KR1IP0126 → {'✅ CORRECT' if abbr_4 == 'KR1IP0126' else '❌ ERREUR'}")
    
    # Test 5: Cache (deuxième appel doit être identique)
    print("\n📌 TEST 5: Vérification du Cache")
    print("-" * 80)
    abbr_5a = cohort_1.get_abbreviation()
    abbr_5b = cohort_1.get_abbreviation()
    print(f"Abréviation 1: {abbr_5a}")
    print(f"Abréviation 2: {abbr_5b}")
    print(f"✓ Cache fonctionne: {'✅ CORRECT' if abbr_5a == abbr_5b else '❌ ERREUR'}")
    
    # Test 6: Années différentes
    print("\n📌 TEST 6: Même cours, mois différent (Février)")
    print("-" * 80)
    cohort_6 = Cohort(
        subject=subject_chinois,
        level=level_3,
        start_date=date(2026, 2, 15),  # Février
        end_date=date(2026, 4, 15),
        teacher=teacher,
        modality='IN_PERSON',
        is_individual=False
    )
    abbr_6 = cohort_6.get_abbreviation()
    print(f"Nom complet: Chinois Niveau 3 (présentiel) - Fév 2026")
    print(f"Abréviation: {abbr_6}")
    print(f"✓ Attendu: CHN3P0226 → {'✅ CORRECT' if abbr_6 == 'CHN3P0226' else '❌ ERREUR'}")
    
    # Test 7: Année différente (2027)
    print("\n📌 TEST 7: Même cours, année différente (2027)")
    print("-" * 80)
    cohort_7 = Cohort(
        subject=subject_japonais,
        level=level_6,
        start_date=date(2027, 1, 20),
        end_date=date(2027, 3, 20),
        teacher=teacher,
        modality='ONLINE',
        is_individual=False
    )
    abbr_7 = cohort_7.get_abbreviation()
    print(f"Nom complet: Japonais Niveau 6 (en ligne) - Jan 2027")
    print(f"Abréviation: {abbr_7}")
    print(f"✓ Attendu: JPN6O0127 → {'✅ CORRECT' if abbr_7 == 'JPN6O0127' else '❌ ERREUR'}")
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    
    results = [
        (abbr_1 == 'CHN3P0126', "Chinois Niveau 3 - Présentiel"),
        (abbr_2 == 'JPN6O0126', "Japonais Niveau 6 - En ligne"),
        (abbr_3 == 'JPN6IO0126', "Japonais Niveau 6 - Individuel en ligne"),
        (abbr_4 == 'KR1IP0126', "Coréen Niveau 1 - Individuel présentiel"),
        (abbr_5a == abbr_5b, "Cache fonctionne"),
        (abbr_6 == 'CHN3P0226', "Changement de mois (février)"),
        (abbr_7 == 'JPN6O0127', "Changement d'année (2027)"),
    ]
    
    passed = sum(1 for result, _ in results if result)
    total = len(results)
    
    for result, description in results:
        status = "✅" if result else "❌"
        print(f"  {status} {description}")
    
    print(f"\n✨ SCORE: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont réussis!")
    else:
        print("⚠️  Certains tests ont échoué.")

except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()
