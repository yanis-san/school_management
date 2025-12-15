from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.hashers import make_password
import random

# Imports basés sur tes fichiers fournis
from core.models import User, Classroom, AcademicYear
from academics.models import Subject, Level, Cohort, WeeklySchedule
from finance.models import Tariff
from students.models import Student, Enrollment

class Command(BaseCommand):
    help = "Seed Data Correct: User(Teacher), AcademicYear, Finance, Cohorts"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Démarrage du Seeding (Correction Code Étudiant)...'))
        self.clear_data()
        
        # 1. Base : Année Scolaire, Salles, Users (Profs)
        year, rooms, teachers = self.create_core_data()
        
        # 2. Finance : Tarifs
        tariffs = self.create_finance_data()
        
        # 3. Académique : Matières, Niveaux, Cohortes
        cohorts = self.create_academic_data(year, rooms, teachers)
        
        # 4. Étudiants & Inscriptions
        self.create_students_enrollments(cohorts, tariffs)
        
        self.stdout.write(self.style.SUCCESS('✅ Base de données prête et cohérente !'))

    def clear_data(self):
        self.stdout.write('   🧹 Nettoyage des données...')
        Enrollment.objects.all().delete()
        Student.objects.all().delete()
        WeeklySchedule.objects.all().delete()
        Cohort.objects.all().delete()
        Subject.objects.all().delete()
        Level.objects.all().delete()
        Tariff.objects.all().delete()
        User.objects.filter(is_teacher=True).delete()
        AcademicYear.objects.all().delete()
        Classroom.objects.all().delete()

    def create_core_data(self):
        self.stdout.write('   🏗️ Création Core (Année, Salles, Profs)...')
        
        year = AcademicYear.objects.create(
            label="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
            is_current=True
        )

        r_tokyo = Classroom.objects.create(name="Salle Tokyo (El Biar)", capacity=12)
        r_zoom = Classroom.objects.create(name="Zoom (En ligne)", capacity=50)

        t_yanis = User.objects.create_user(
            username="yanis_sensei", email="yanis@torii.dz", password="password123",
            first_name="Yanis", last_name="Sensei", is_teacher=True, phone="0550111111"
        )
        
        t_wei = User.objects.create_user(
            username="wei_laoshi", email="wei@torii.dz", password="password123",
            first_name="Wei", last_name="Zhang", is_teacher=True, phone="0550222222"
        )
        
        t_minji = User.objects.create_user(
            username="minji_saem", email="minji@torii.dz", password="password123",
            first_name="Min-Ji", last_name="Kim", is_teacher=True, phone="0550333333"
        )

        return year, [r_tokyo, r_zoom], {"yanis": t_yanis, "wei": t_wei, "minji": t_minji}

    def create_finance_data(self):
        self.stdout.write('   💰 Création Finance (Tarifs)...')
        t_std = Tariff.objects.create(name="Standard Session", amount=30000.00)
        t_stud = Tariff.objects.create(name="Étudiant Session", amount=25000.00)
        t_pack = Tariff.objects.create(name="Pack Privé 10h", amount=40000.00)
        
        return {"std": t_std, "stud": t_stud, "pack": t_pack}

    def create_academic_data(self, year, rooms, teachers):
        self.stdout.write('   🏫 Création Académique (Matières, Niveaux, Cohortes)...')
        r_tokyo, r_zoom = rooms
        
        s_jap = Subject.objects.create(name="Japonais")
        s_kor = Subject.objects.create(name="Coréen")
        s_chi = Subject.objects.create(name="Chinois")
        
        l_n5 = Level.objects.create(name="N5")
        l_topik = Level.objects.create(name="Débutant")
        l_hsk = Level.objects.create(name="HSK 1")

        # 1. Japonais Présentiel
        c_jap = Cohort.objects.create(
            name="Japonais N5 - Samedi",
            subject=s_jap, level=l_n5, academic_year=year, teacher=teachers['yanis'],
            start_date=date.today(), end_date=date.today() + timedelta(days=90),
            standard_price=30000.00
        )
        WeeklySchedule.objects.create(cohort=c_jap, day_of_week=5, start_time="09:00", end_time="12:00", classroom=r_tokyo)

        # 2. Coréen En Ligne
        c_kor = Cohort.objects.create(
            name="Coréen Soir - Zoom",
            subject=s_kor, level=l_topik, academic_year=year, teacher=teachers['minji'],
            start_date=date.today(), end_date=date.today() + timedelta(days=90),
            standard_price=25000.00
        )
        WeeklySchedule.objects.create(cohort=c_kor, day_of_week=1, start_time="19:00", end_time="20:30", classroom=r_zoom)

        # 3. Chinois Privé
        c_chi = Cohort.objects.create(
            name="Coaching Chinois",
            subject=s_chi, level=l_hsk, academic_year=year, teacher=teachers['wei'],
            start_date=date.today(), end_date=date.today() + timedelta(days=90),
            standard_price=40000.00
        )

        return [c_jap, c_kor, c_chi]

    def create_students_enrollments(self, cohorts, tariffs):
        self.stdout.write('   🎓 Création Étudiants (Avec Codes Uniques)...')
        c_jap, c_kor, c_chi = cohorts
        
        # J'ajoute student_code manuellement pour éviter l'erreur UNIQUE
        
        # 1. Amine
        s1 = Student.objects.create(
            first_name="Amine", last_name="Benali", phone="05501", 
            email="amine@test.com", 
            student_code="2025-001" # <--- AJOUTÉ
        )
        Enrollment.objects.create(student=s1, cohort=c_jap, tariff=tariffs['std'], payment_plan='FULL')

        # 2. Sarah
        s2 = Student.objects.create(
            first_name="Sarah", last_name="Mokhtari", phone="05502", 
            email="sarah@test.com",
            student_code="2025-002" # <--- AJOUTÉ (différent du premier)
        )
        Enrollment.objects.create(student=s2, cohort=c_jap, tariff=tariffs['stud'], payment_plan='MONTHLY')

        # 3. Lina
        s3 = Student.objects.create(
            first_name="Lina", last_name="Bouchama", phone="05503", 
            email="lina@test.com",
            student_code="2025-003" # <--- AJOUTÉ
        )
        Enrollment.objects.create(
            student=s3, cohort=c_chi, tariff=tariffs['pack'], 
            payment_plan='PACK', hours_purchased=10, hours_consumed=0
        )