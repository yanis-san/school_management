# students/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, time
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import User, AcademicYear, Classroom
from academics.models import Subject, Level, Cohort
from students.models import Student, Enrollment
from finance.models import Tariff, Payment


class StudentModelTest(TestCase):
    """Tests pour le modèle Student"""

    def setUp(self):
        self.student = Student.objects.create(
            first_name="Alice", last_name="Durand", phone="0555123456", phone_2="", email="alice@example.com", student_code="ST-TEST-001", birth_date=date(2005, 3, 15)
        )

    def test_01_student_creation(self):
        """Test la création d'un étudiant"""
        print("\n[TEST] Test 1: Création d'un étudiant")

        self.assertEqual(self.student.first_name, "Alice")
        self.assertEqual(self.student.last_name, "Durand")
        self.assertEqual(self.student.phone, "0555123456")
        self.assertTrue(self.student.student_code)  # Code auto-généré

        print(f"   ✅ Étudiant créé: {self.student.first_name} {self.student.last_name}")
        print(f"   ✅ Code étudiant: {self.student.student_code}")

    def test_02_student_code_uniqueness(self):
        """Test l'unicité du code étudiant"""
        print("\n[TEST] Test 2: Unicité du code étudiant")

        student2 = Student.objects.create(
            first_name="Bob", last_name="Martin", phone="0555654321", phone_2="", student_code="ST-TEST-002", birth_date=date(2006, 7, 22)
        )

        # Les codes doivent être différents
        self.assertNotEqual(self.student.student_code, student2.student_code)

        print(f"   ✅ Codes uniques: {self.student.student_code} != {student2.student_code}")

    def test_03_student_full_name(self):
        """Test la méthode __str__"""
        print("\n[TEST] Test 3: Représentation string de l'étudiant")

        expected = "DURAND Alice"
        self.assertEqual(str(self.student), expected)

        print(f"   ✅ Représentation: {str(self.student)}")


class StudentProfilePictureTest(TestCase):
    """Tests pour les photos de profil des étudiants"""

    def setUp(self):
        self.student = Student.objects.create(
            first_name="Test", last_name="Student", phone="0555000000", phone_2="", student_code="ST-TEST-003", birth_date=date(2005, 1, 1)
        )

    def create_test_image(self):
        """Crée une image de test en mémoire"""
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(file, 'png')
        file.name = 'test_student.png'
        file.seek(0)
        return SimpleUploadedFile(
            name='test_student.png',
            content=file.read(),
            content_type='image/png'
        )

    def test_01_student_profile_picture_upload(self):
        """Test l'upload d'une photo de profil étudiant"""
        print("\n[TEST] Test 1: Upload photo de profil étudiant")

        # Initialement, pas de photo
        self.assertFalse(self.student.profile_picture)

        # Upload d'une photo
        test_image = self.create_test_image()
        self.student.profile_picture = test_image
        self.student.save()

        # Vérifier que la photo est bien enregistrée
        self.student.refresh_from_db()
        self.assertTrue(self.student.profile_picture)
        self.assertIn('profiles/students/', self.student.profile_picture.name)

        print(f"   ✅ Photo uploadée: {self.student.profile_picture.name}")


class EnrollmentTest(TestCase):
    """Tests pour le modèle Enrollment"""

    def setUp(self):
        # Setup de base
        self.ay = AcademicYear.objects.create(
            label="2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        self.teacher = User.objects.create_user(
            username="teacher",
            is_teacher=True,
            birth_date=date(1985, 5, 15)
        )
        self.subject = Subject.objects.create(name="Français")
        self.level = Level.objects.create(name="Seconde")
        self.cohort = Cohort.objects.create(
            name="Français Seconde",
            subject=self.subject,
            level=self.level,
            teacher=self.teacher,
            academic_year=self.ay,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            teacher_hourly_rate=1800
        )
        self.student = Student.objects.create(
            first_name="Alice", last_name="Durand", phone="0555111111", phone_2="", student_code="ST-TEST-004", birth_date=date(2005, 3, 15)
        )
        self.tariff = Tariff.objects.create(name="Standard", amount=8000)

    def test_01_enrollment_creation(self):
        """Test la création d'une inscription"""
        print("\n[TEST] Test 1: Création d'une inscription")

        enrollment = Enrollment.objects.create(
            student=self.student,
            cohort=self.cohort,
            tariff=self.tariff,
            payment_plan='FULL'
        )

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.cohort, self.cohort)
        self.assertEqual(enrollment.balance_due, 8000)  # Montant initial du tarif

        print(f"   ✅ Inscription créée pour {self.student} dans {self.cohort}")
        print(f"   ✅ Montant dû: {enrollment.balance_due} DA")

    def test_02_enrollment_balance_after_payment(self):
        """Test le calcul du solde après paiement"""
        print("\n[TEST] Test 2: Calcul du solde après paiement")

        enrollment = Enrollment.objects.create(
            student=self.student,
            cohort=self.cohort,
            tariff=self.tariff,
            payment_plan='FULL'
        )

        # Paiement de 3000 DA
        Payment.objects.create(
            enrollment=enrollment,
            amount=3000,
            method='CASH',
            recorded_by=self.teacher
        )

        # Le solde devrait être 8000 - 3000 = 5000
        self.assertEqual(enrollment.balance_due, 5000)

        print(f"   ✅ Après paiement de 3000 DA, reste: {enrollment.balance_due} DA")


class StudentListViewTest(TestCase):
    """Tests pour la vue de liste des étudiants"""

    def setUp(self):
        # Créer des étudiants
        self.student1 = Student.objects.create(
            first_name="Alice", last_name="Durand", phone="0555111111", phone_2="", student_code="ST-TEST-004",
            email="alice@test.com", birth_date=date(2005, 3, 15)
        )
        self.student2 = Student.objects.create(
            first_name="Bob", last_name="Martin", phone="0555222222", phone_2="", email="bob@test.com", student_code="ST-TEST-005", birth_date=date(2006, 7, 22)
        )

        # Créer un utilisateur admin pour se connecter
        self.admin = User.objects.create_user(
            username="admin",
            password="test123",
            is_staff=True,
            is_superuser=True,
            birth_date=date(1980, 1, 10)
        )

        self.client = Client()
        self.client.login(username='admin', password='test123')

    def test_01_student_list_view_loads(self):
        """Test que la page de liste se charge correctement"""
        print("\n[TEST] Test 1: Chargement de la liste des étudiants")

        response = self.client.get(reverse('students:list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('students', response.context)

        # Vérifier que les 2 étudiants sont présents
        students = response.context['students']
        self.assertEqual(students.paginator.count, 2)

        print(f"   ✅ Page chargée avec {students.paginator.count} étudiants")

    def test_02_student_search(self):
        """Test la recherche d'étudiants"""
        print("\n[TEST] Test 2: Recherche d'étudiants")

        # Recherche par prénom
        response = self.client.get(reverse('students:list'), {'q': 'Alice'})

        students = response.context['students']
        self.assertEqual(students.paginator.count, 1)
        self.assertEqual(students.object_list[0].first_name, "Alice")

        print(f"   ✅ Recherche 'Alice' trouvée: {students.object_list[0]}")

    def test_03_student_filter_by_cohort(self):
        """Test le filtrage par groupe"""
        print("\n[TEST] Test 3: Filtrage par groupe")

        # Setup: créer un groupe et inscrire un étudiant
        ay = AcademicYear.objects.create(
            label="2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        teacher = User.objects.create_user(username="teacher", is_teacher=True, birth_date=date(1985, 5, 15))
        subject = Subject.objects.create(name="Math")
        level = Level.objects.create(name="Terminale")
        cohort = Cohort.objects.create(
            name="Math Term",
            subject=subject,
            level=level,
            teacher=teacher,
            academic_year=ay,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            teacher_hourly_rate=2000
        )
        tariff = Tariff.objects.create(name="Standard", amount=5000)

        Enrollment.objects.create(
            student=self.student1,
            cohort=cohort,
            tariff=tariff,
            payment_plan='FULL'
        )

        # Filtrer par ce groupe
        response = self.client.get(reverse('students:list'), {'cohort': cohort.id})

        students = response.context['students']
        self.assertEqual(students.paginator.count, 1)
        self.assertEqual(students.object_list[0], self.student1)

        print(f"   ✅ Filtrage par '{cohort.name}' trouvé: {students.object_list[0]}")


class StudentDetailViewTest(TestCase):
    """Tests pour la vue de détail d'un étudiant"""

    def setUp(self):
        self.student = Student.objects.create(
            first_name="Alice",
            last_name="Durand",
            phone="0555123456",
            phone_2="",
            email="alice@test.com",
            birth_date=date(2005, 3, 15)
        )

        # Créer un groupe et une inscription
        self.ay = AcademicYear.objects.create(
            label="2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        self.teacher = User.objects.create_user(username="teacher", is_teacher=True, birth_date=date(1985, 5, 15))
        self.subject = Subject.objects.create(name="Anglais")
        self.level = Level.objects.create(name="B1")
        self.cohort = Cohort.objects.create(
            name="Anglais B1",
            subject=self.subject,
            level=self.level,
            teacher=self.teacher,
            academic_year=self.ay,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            teacher_hourly_rate=1500
        )
        self.tariff = Tariff.objects.create(name="Standard", amount=7000)

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            cohort=self.cohort,
            tariff=self.tariff,
            payment_plan='FULL'
        )

        # Créer un admin pour se connecter
        self.admin = User.objects.create_user(
            username="admin",
            password="test123",
            is_staff=True,
            is_superuser=True,
            birth_date=date(1980, 1, 10)
        )

        self.client = Client()
        self.client.login(username='admin', password='test123')

    def test_01_student_detail_view_loads(self):
        """Test que la page de détail se charge"""
        print("\n[TEST] Test 1: Chargement de la page de détail")

        response = self.client.get(reverse('students:detail', args=[self.student.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student'], self.student)

        print(f"   ✅ Page de détail chargée pour {self.student}")

    def test_02_enrollments_displayed(self):
        """Test que les inscriptions sont affichées"""
        print("\n[TEST] Test 2: Affichage des inscriptions")

        response = self.client.get(reverse('students:detail', args=[self.student.id]))

        enrollments = response.context['enrollments']
        self.assertEqual(enrollments.count(), 1)
        self.assertEqual(enrollments.first().cohort, self.cohort)

        print(f"   ✅ 1 inscription affichée: {enrollments.first().cohort.name}")

    def test_03_balance_displayed(self):
        """Test que le solde est affiché correctement"""
        print("\n[TEST] Test 3: Affichage du solde")

        response = self.client.get(reverse('students:detail', args=[self.student.id]))

        enrollments = response.context['enrollments']
        enrollment = enrollments.first()

        # Le solde initial devrait être égal au tarif
        self.assertEqual(enrollment.balance_due, 7000)

        print(f"   ✅ Solde affiché: {enrollment.balance_due} DA")

    def test_04_payments_history_displayed(self):
        """Test que l'historique des paiements est affiché"""
        print("\n[TEST] Test 4: Affichage de l'historique des paiements")

        # Ajouter quelques paiements
        Payment.objects.create(
            enrollment=self.enrollment,
            amount=2000,
            method='CASH',
            recorded_by=self.teacher
        )
        Payment.objects.create(
            enrollment=self.enrollment,
            amount=3000,
            method='TRANSFER',
            recorded_by=self.teacher
        )

        response = self.client.get(reverse('students:detail', args=[self.student.id]))

        enrollments = response.context['enrollments']
        enrollment = enrollments.first()
        payments = enrollment.payments.all()

        self.assertEqual(payments.count(), 2)
        self.assertEqual(enrollment.balance_due, 2000)  # 7000 - 2000 - 3000

        print(f"   ✅ {payments.count()} paiements affichés")
        print(f"   ✅ Solde restant: {enrollment.balance_due} DA")
