# academics/tests.py
from django.test import TestCase
from datetime import date, time, timedelta
from core.models import User, AcademicYear, Classroom
from academics.models import Subject, Level, Cohort, WeeklySchedule, CourseSession
from students.models import Student, Enrollment
from finance.models import Tariff, Installment

class SchoolSystemTest(TestCase):

    def setUp(self):
        """Préparation des données avant chaque test"""
        # 1. Setup Core
        self.ay = AcademicYear.objects.create(
            label="2024", 
            start_date=date(2024,1,1), 
            end_date=date(2024,12,31)
        )
        self.room = Classroom.objects.create(name="Salle A")
        
        # 2. Profs (On met un taux par défaut, mais le groupe l'écrasera)
        self.prof1 = User.objects.create_user(username="prof1", is_teacher=True, birth_date=date(1985, 5, 15))
        self.prof_sub = User.objects.create_user(username="prof_sub", is_teacher=True, birth_date=date(1990, 3, 20))
        
        # 3. Academics Base
        self.subj = Subject.objects.create(name="Japonais")
        self.lvl = Level.objects.create(name="N5")

        # 4. Le Groupe (Cohort)
        # On définit ici le TARIF DU GROUPE (ex: 1500 DA/h)
        self.cohort = Cohort.objects.create(
            name="Jap N5 Test",
            subject=self.subj,
            level=self.lvl,
            teacher=self.prof1,
            substitute_teacher=self.prof_sub,
            start_date=date(2024, 1, 1), # Lundi
            end_date=date(2024, 1, 31),  # 1 mois
            academic_year=self.ay,
            teacher_hourly_rate=1500 # <--- LE TAUX QUI COMPTE
        )

        # 5. Planning : Lundi 10h00 - 12h00 (2h00)
        WeeklySchedule.objects.create(
            cohort=self.cohort, 
            day_of_week=0, # Lundi
            start_time=time(10,0), 
            end_time=time(12,0), 
            classroom=self.room
        )

    def calculate_teacher_pay(self, teacher_user):
        """
        Fonction utilitaire pour calculer la paie exacte
        Formule : Somme des (Durée Séance * Taux Groupe)
        """
        sessions = CourseSession.objects.filter(
            teacher=teacher_user, 
            status='COMPLETED',
            # teacher_payments__isnull=True 
        )
        
        total_pay = 0
        for sess in sessions:
            # Calcul durée précise (en heures décimales)
            t1 = sess.start_time
            t2 = sess.end_time
            
            # Conversion en minutes pour être précis
            minutes_duration = (t2.hour * 60 + t2.minute) - (t1.hour * 60 + t1.minute)
            hours_duration = minutes_duration / 60.0
            
            # Récupération du taux du GROUPE
            rate = float(sess.cohort.teacher_hourly_rate)
            
            total_pay += hours_duration * rate
            
        return total_pay

    def test_01_automatic_scheduling(self):
        """Test si les séances sont générées automatiquement"""
        print("\n[TEST] Test 1: Generation Planning Auto")
        self.cohort.schedule_generated = True
        self.cohort.save()
        
        sessions = CourseSession.objects.filter(cohort=self.cohort)
        self.assertTrue(sessions.count() > 0)
        print(f"   ✅ {sessions.count()} Séances générées")


    def test_02_rescheduling_logic(self):
        """Test si reporter une séance crée bien un rattrapage AUTOMATIQUE"""
        print("\n[TEST] Test 2: Report Automatique & Rattrapage")
        
        self.cohort.schedule_generated = True
        self.cohort.save()
        
        # On prend la première séance
        session = CourseSession.objects.filter(cohort=self.cohort).first()
        original_count = CourseSession.objects.filter(cohort=self.cohort).count()
        original_end_date = self.cohort.end_date

        print(f"   --- Avant : {original_count} séances. Fin du groupe : {original_end_date}")

        # Action : On la reporte (POSTPONED)
        session.status = 'POSTPONED'
        session.save() # [TEST] Le Signal doit se déclencher ici

        # Vérification 1 : Une nouvelle séance a-t-elle été créée ?
        new_count = CourseSession.objects.filter(cohort=self.cohort).count()
        self.assertEqual(new_count, original_count + 1)
        
        # Vérification 2 : La nouvelle séance est-elle bien APRÈS la fin théorique ?
        # On recharge le groupe depuis la BDD car la date de fin a dû changer
        self.cohort.refresh_from_db()
        last_session = CourseSession.objects.filter(cohort=self.cohort).last()
        
        self.assertTrue(last_session.date > original_end_date)
        print(f"   ✅ Séance reportée. Rattrapage créé le {last_session.date}")
        print(f"   ✅ La date de fin du groupe a été repoussée au {self.cohort.end_date}")

    def test_04_teacher_payroll_calculation_volume(self):
        """
        Test CRITIQUE : Calcul sur le volume horaire
        Scénario : 
        - Le cours fait 2h00.
        - Le taux est de 1500 DA/h.
        - Le prof fait 4 séances complètes.
        - Calcul attendu : 4 séances * 2 heures * 1500 DA = 12 000 DA
        """
        print("\n[TEST] Test 4: Calcul Paie Prof (Volume Horaire)")
        
        # 1. Générer les séances
        self.cohort.schedule_generated = True
        self.cohort.save()

        # 2. Simuler que le prof a fait les 4 premières séances
        sessions = CourseSession.objects.filter(cohort=self.cohort).order_by('date')[:4]
        for s in sessions:
            s.status = 'COMPLETED'
            s.save()
            
        # 3. Calculer
        amount_due = self.calculate_teacher_pay(self.prof1)
        
        # 4. Vérifier
        # 4 séances * 2 heures * 1500 DA = 12000
        expected_amount = 4 * 2.0 * 1500
        
        self.assertEqual(amount_due, expected_amount)
        print(f"   ✅ Calcul validé : 4 séances de 2h à 1500da/h = {amount_due} DA")

    def test_05_teacher_payroll_mixed_duration(self):
        """
        Test CRITIQUE 2 : Changement de durée
        Scénario : Une séance dure exceptionnellement 3h au lieu de 2h.
        """
        print("\n[TEST] Test 5: Calcul Paie avec durée variable")
        self.cohort.schedule_generated = True
        self.cohort.save()
        
        # On prend une séance
        session = CourseSession.objects.first()
        session.status = 'COMPLETED'
        
        # MODIFICATION : Cette séance a duré 3h (10h-13h) au lieu de 2h
        session.end_time = time(13, 0) 
        session.save()
        
        amount_due = self.calculate_teacher_pay(self.prof1)
        
        # Attendu : 3 heures * 1500 = 4500 DA
        self.assertEqual(amount_due, 4500)
        print(f"   ✅ Calcul validé pour durée modifiée (3h) : {amount_due} DA")


class AcademicsViewsTest(TestCase):
    """Tests pour les nouvelles vues du module academics"""

    def setUp(self):
        # Setup de base
        self.ay = AcademicYear.objects.create(
            label="2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        self.room = Classroom.objects.create(name="Salle Test")
        self.teacher = User.objects.create_user(
            username="teacher",
            password="test123",
            is_teacher=True,
            birth_date=date(1985, 5, 15)
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="test123",
            is_staff=True,
            is_superuser=True,
            birth_date=date(1980, 1, 10)
        )
        self.subject = Subject.objects.create(name="Physique")
        self.level = Level.objects.create(name="Première")

        self.cohort = Cohort.objects.create(
            name="Physique Première",
            subject=self.subject,
            level=self.level,
            teacher=self.teacher,
            academic_year=self.ay,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            teacher_hourly_rate=2500
        )

        # Créer un planning hebdomadaire
        WeeklySchedule.objects.create(
            cohort=self.cohort,
            day_of_week=0,  # Lundi
            start_time=time(9, 0),
            end_time=time(11, 0),
            classroom=self.room
        )

        from django.test import Client
        self.client = Client()

    def test_01_cohort_list_view(self):
        """Test la vue liste des groupes"""
        print("\n[TEST] Test 1: Vue liste des groupes")

        self.client.login(username='admin', password='test123')
        from django.urls import reverse
        response = self.client.get(reverse('academics:list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('cohorts', response.context)

        cohorts = response.context['cohorts']
        self.assertEqual(cohorts.count(), 1)
        self.assertEqual(cohorts.first(), self.cohort)

        print(f"   ✅ Liste chargée avec {cohorts.count()} groupe(s)")

    def test_02_cohort_detail_view(self):
        """Test la vue détail d'un groupe"""
        print("\n[TEST] Test 2: Vue détail d'un groupe")

        self.client.login(username='admin', password='test123')
        from django.urls import reverse
        response = self.client.get(reverse('academics:detail', args=[self.cohort.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cohort'], self.cohort)

        print(f"   ✅ Détail du groupe '{self.cohort.name}' chargé")

    def test_03_generate_sessions_view(self):
        """Test la génération de séances via la vue"""
        print("\n[TEST] Test 3: Génération de séances via POST")

        self.client.login(username='admin', password='test123')
        from django.urls import reverse

        # Vérifier qu'il n'y a pas encore de séances
        self.assertEqual(CourseSession.objects.filter(cohort=self.cohort).count(), 0)
        self.assertFalse(self.cohort.schedule_generated)

        # Déclencher la génération
        response = self.client.post(reverse('academics:generate_sessions', args=[self.cohort.id]))

        # Devrait rediriger vers la page de détail
        self.assertEqual(response.status_code, 302)

        # Vérifier que les séances ont été créées
        self.cohort.refresh_from_db()
        self.assertTrue(self.cohort.schedule_generated)

        sessions = CourseSession.objects.filter(cohort=self.cohort)
        self.assertTrue(sessions.count() > 0)

        print(f"   ✅ {sessions.count()} séances générées automatiquement")

    def test_04_session_detail_view_get(self):
        """Test la vue de détail d'une séance (GET)"""
        print("\n[TEST] Test 4: Affichage du formulaire de présence")

        # Générer des séances
        self.cohort.schedule_generated = True
        self.cohort.save()

        session = CourseSession.objects.filter(cohort=self.cohort).first()

        # Créer des étudiants et inscriptions
        tariff = Tariff.objects.create(name="Standard", amount=5000)
        student1 = Student.objects.create(first_name="Alice", last_name="Test", phone="0555111111", phone_2="", student_code="ST-ACAD-001", birth_date=date(2005, 3, 15))
        student2 = Student.objects.create(first_name="Bob", last_name="Test", phone="0555222222", phone_2="", student_code="ST-ACAD-002", birth_date=date(2006, 7, 22))

        Enrollment.objects.create(student=student1, cohort=self.cohort, tariff=tariff, payment_plan='FULL')
        Enrollment.objects.create(student=student2, cohort=self.cohort, tariff=tariff, payment_plan='FULL')

        self.client.login(username='teacher', password='test123')
        from django.urls import reverse
        response = self.client.get(reverse('academics:session_detail', args=[session.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['session'], session)

        # Vérifier que les inscriptions sont dans le contexte
        enrollments = response.context['enrollments']
        self.assertEqual(enrollments.count(), 2)

        print(f"   ✅ Formulaire chargé avec {enrollments.count()} étudiants")

    def test_05_session_detail_view_post_attendance(self):
        """Test l'enregistrement des présences via POST"""
        print("\n[TEST] Test 5: Enregistrement des présences")

        # Générer des séances
        self.cohort.schedule_generated = True
        self.cohort.save()

        session = CourseSession.objects.filter(cohort=self.cohort).first()
        session.status = 'SCHEDULED'
        session.save()

        # Créer des étudiants et inscriptions
        tariff = Tariff.objects.create(name="Standard", amount=5000)
        student1 = Student.objects.create(first_name="Alice", last_name="Test", phone="0555111111", phone_2="", student_code="ST-ACAD-001", birth_date=date(2005, 3, 15))
        student2 = Student.objects.create(first_name="Bob", last_name="Test", phone="0555222222", phone_2="", student_code="ST-ACAD-002", birth_date=date(2006, 7, 22))

        enrollment1 = Enrollment.objects.create(student=student1, cohort=self.cohort, tariff=tariff, payment_plan='FULL')
        enrollment2 = Enrollment.objects.create(student=student2, cohort=self.cohort, tariff=tariff, payment_plan='FULL')

        self.client.login(username='teacher', password='test123')
        from django.urls import reverse

        # Soumettre les présences
        post_data = {
            'session_note': 'Cours complet',
            f'status_{student1.id}': 'PRESENT',
            f'status_{student2.id}': 'ABSENT'
        }

        response = self.client.post(reverse('academics:session_detail', args=[session.id]), post_data)

        # Devrait rediriger après succès
        self.assertEqual(response.status_code, 302)

        # Vérifier que la session est marquée comme complétée
        session.refresh_from_db()
        self.assertEqual(session.status, 'COMPLETED')
        self.assertEqual(session.note, 'Cours complet')

        # Vérifier que les présences ont été enregistrées
        from students.models import Attendance
        attendances = Attendance.objects.filter(session=session)
        self.assertEqual(attendances.count(), 2)

        attendance1 = attendances.get(enrollment=enrollment1)
        attendance2 = attendances.get(enrollment=enrollment2)

        self.assertEqual(attendance1.status, 'PRESENT')
        self.assertEqual(attendance2.status, 'ABSENT')

        print(f"   ✅ {attendances.count()} présences enregistrées")
        print(f"   ✅ Session marquée comme: {session.status}")


