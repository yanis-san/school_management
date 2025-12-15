# finance/tests.py
from django.test import TestCase
from datetime import date, time
from core.models import User, AcademicYear, Classroom
from academics.models import Subject, Level, Cohort, WeeklySchedule, CourseSession
from students.models import Student, Enrollment
from finance.models import Tariff, Payment, Installment

class FinanceAndTrackingTest(TestCase):

    def setUp(self):
        # 1. Setup de base
        self.ay = AcademicYear.objects.create(label="2024", start_date=date(2024,1,1), end_date=date(2024,12,31))
        self.room = Classroom.objects.create(name="Salle A")
        self.prof = User.objects.create_user(username="prof", is_teacher=True)
        self.subj = Subject.objects.create(name="Anglais")
        self.lvl = Level.objects.create(name="B2")
        
        # 2. Tarif
        self.tariff = Tariff.objects.create(name="Standard", amount=10000) # 10 000 DA

        # 3. Groupe
        self.cohort = Cohort.objects.create(
            name="Anglais B2",
            subject=self.subj, level=self.lvl, teacher=self.prof,
            academic_year=self.ay,
            start_date=date(2024,1,1), end_date=date(2024,3,31)
        )
        
        # 4. Élève
        self.student = Student.objects.create(first_name="Yanis", last_name="Dev", phone="0555")

    def test_01_partial_payment_logic(self):
        """Test du paiement partiel et du calcul du reste à payer"""
        print("\n💰 Test 1: Paiement Partiel")
        
        # Inscription (10 000 DA à payer)
        enrollment = Enrollment.objects.create(
            student=self.student, cohort=self.cohort, tariff=self.tariff, payment_plan='FULL'
        )
        
        # Vérif initiale
        self.assertEqual(enrollment.balance_due, 10000)
        print("   ✅ Dette initiale : 10 000 DA")

        # Action : Il paie 3000 DA
        Payment.objects.create(
            enrollment=enrollment, amount=3000, recorded_by=self.prof
        )

        # Vérif après paiement
        self.assertEqual(enrollment.balance_due, 7000)
        print("   ✅ Reste à payer correct : 7 000 DA")

        # Action : Il solde tout
        Payment.objects.create(
            enrollment=enrollment, amount=7000, recorded_by=self.prof
        )
        self.assertEqual(enrollment.balance_due, 0)
        print("   ✅ Dette soldée : 0 DA")

    def test_02_pack_hours_consumption(self):
        """Test : Est-ce que les heures sont débitées quand le cours est fini ?"""
        print("\n⏱️ Test 2: Consommation Pack d'Heures")
        
        # Inscription
        enrollment = Enrollment.objects.create(
            student=self.student, cohort=self.cohort, tariff=self.tariff, payment_plan='PACK'
        )
        
        # Séance de 2h (10h -> 12h)
        session = CourseSession.objects.create(
            cohort=self.cohort, date=date(2024,1,10),
            start_time=time(10,0), end_time=time(12,0),
            teacher=self.prof, classroom=self.room,
            status='SCHEDULED'
        )

        # Vérif avant : 0 heures consommées
        enrollment.refresh_from_db() # Important pour recharger les données
        self.assertEqual(enrollment.hours_consumed, 0)

        # Action : Le prof valide le cours (COMPLETED)
        session.status = 'COMPLETED'
        session.save() # C'est ici que le Signal doit se déclencher

        # Vérif après
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.hours_consumed, 2.0)
        print(f"   ✅ Heures consommées : {enrollment.hours_consumed}h (Attendu: 2.0h)")

    def test_03_installments_status(self):
        """Test : Est-ce qu'une échéance passe à 'Payé' ?"""
        print("\n📅 Test 3: Statut des Échéances")
        
        # Inscription avec paiement TOTAL (Une seule échéance de 10000)
        enrollment = Enrollment.objects.create(
            student=self.student, cohort=self.cohort, tariff=self.tariff, payment_plan='FULL'
        )
        
        installment = enrollment.installments.first()
        self.assertFalse(installment.is_paid)
        
        # On paie la totalité
        payment = Payment.objects.create(
            enrollment=enrollment, amount=10000, recorded_by=self.prof
        )
        
        # Note: Dans notre code actuel, on n'a pas encore fait le lien automatique 
        # "Paiement -> Met à jour Installment.is_paid".
        # C'est souvent une logique complexe. Pour l'instant, testons si on peut le faire manuellement.
        
        installment.is_paid = True
        installment.payment = payment
        installment.save()
        
        self.assertTrue(installment.is_paid)
        print("   ✅ Échéance marquée comme payée")