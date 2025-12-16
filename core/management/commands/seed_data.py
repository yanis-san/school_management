from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from django.contrib.auth.hashers import make_password
import random

# Imports basés sur tes fichiers fournis
from core.models import User, Classroom, AcademicYear, TeacherProfile
from academics.models import Subject, Level, Cohort, WeeklySchedule, CourseSession
from finance.models import Tariff, Discount, Payment, TeacherPayment
from students.models import Student, Enrollment, Attendance

class Command(BaseCommand):
    help = "Seed Data Complet avec TeacherProfile, Paiements, Sessions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Démarrage du Seeding Complet...'))
        self.clear_data()

        # 1. Base : Admin
        admin = self.create_admin()

        # 2. Base : Année Scolaire, Salles, Users (Profs)
        year, rooms, teachers = self.create_core_data()

        # 3. Finance : Tarifs & Réductions
        tariffs, discounts = self.create_finance_data()

        # 4. Académique : Matières, Niveaux, Cohortes
        cohorts = self.create_academic_data(year, rooms, teachers)

        # 5. Génération des séances
        self.generate_sessions(cohorts)

        # 6. Étudiants & Inscriptions
        self.create_students_enrollments(cohorts, tariffs)

        # 7. Complétion de séances passées
        self.complete_past_sessions(cohorts)

        # 8. Génération des paiements étudiants
        self.generate_student_payments(admin)

        # 9. Génération des paiements professeurs
        self.generate_teacher_payments(teachers, admin)

        self.print_summary()
        self.stdout.write(self.style.SUCCESS('✅ Base de données prête et cohérente !'))

    def clear_data(self):
        self.stdout.write('   🧹 Nettoyage des données...')
        TeacherPayment.objects.all().delete()
        Payment.objects.all().delete()
        Attendance.objects.all().delete()
        Enrollment.objects.all().delete()
        Student.objects.all().delete()
        CourseSession.objects.all().delete()
        WeeklySchedule.objects.all().delete()
        Cohort.objects.all().delete()
        Subject.objects.all().delete()
        Level.objects.all().delete()
        Discount.objects.all().delete()
        Tariff.objects.all().delete()
        TeacherProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        AcademicYear.objects.all().delete()
        Classroom.objects.all().delete()

    def create_admin(self):
        self.stdout.write('   👤 Création Admin...')
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@school.dz',
                'first_name': 'Admin',
                'last_name': 'System',
                'phone': '0550000000',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        return admin

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

        # Créer les profils professeurs
        TeacherProfile.objects.create(
            user=t_yanis, preferred_payment_method='TRANSFER',
            bank_details='CCP 0021567890123', tax_id='199812345678901'
        )
        TeacherProfile.objects.create(
            user=t_wei, preferred_payment_method='CHECK',
            bank_details='RIB 00799999001234567890123', tax_id='199634567890123'
        )
        TeacherProfile.objects.create(
            user=t_minji, preferred_payment_method='CASH', tax_id='199723456789012'
        )

        return year, [r_tokyo, r_zoom], {"yanis": t_yanis, "wei": t_wei, "minji": t_minji}

    def create_finance_data(self):
        self.stdout.write('   💰 Création Finance (Tarifs & Réductions)...')
        t_std = Tariff.objects.create(name="Standard Session", amount=30000.00)
        t_stud = Tariff.objects.create(name="Étudiant Session", amount=25000.00)
        t_pack = Tariff.objects.create(name="Pack Privé 10h", amount=40000.00)

        d_fratrie = Discount.objects.create(name="Réduction Fratrie", value=10, type='PERCENT', is_active=True)

        return {"std": t_std, "stud": t_stud, "pack": t_pack}, [d_fratrie]

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
            start_date=date.today() - timedelta(days=60), end_date=date.today() + timedelta(days=30),
            standard_price=30000.00, teacher_hourly_rate=1500.00,
            schedule_generated=False
        )
        WeeklySchedule.objects.create(cohort=c_jap, day_of_week=5, start_time=time(9,0), end_time=time(12,0), classroom=r_tokyo)

        # 2. Coréen En Ligne
        c_kor = Cohort.objects.create(
            name="Coréen Soir - Zoom",
            subject=s_kor, level=l_topik, academic_year=year, teacher=teachers['minji'],
            start_date=date.today() - timedelta(days=45), end_date=date.today() + timedelta(days=45),
            standard_price=25000.00, teacher_hourly_rate=1200.00,
            schedule_generated=False
        )
        WeeklySchedule.objects.create(cohort=c_kor, day_of_week=1, start_time=time(19,0), end_time=time(20,30), classroom=r_zoom)

        # 3. Chinois Privé
        c_chi = Cohort.objects.create(
            name="Coaching Chinois",
            subject=s_chi, level=l_hsk, academic_year=year, teacher=teachers['wei'],
            start_date=date.today() - timedelta(days=30), end_date=date.today() + timedelta(days=60),
            standard_price=40000.00, teacher_hourly_rate=1800.00,
            schedule_generated=False
        )
        WeeklySchedule.objects.create(cohort=c_chi, day_of_week=6, start_time=time(14,0), end_time=time(17,0), classroom=r_tokyo)

        return [c_jap, c_kor, c_chi]

    def generate_sessions(self, cohorts):
        self.stdout.write('   📅 Génération des séances...')
        for cohort in cohorts:
            cohort.schedule_generated = True
            cohort.save()

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

    def complete_past_sessions(self, cohorts):
        self.stdout.write('   ✅ Complétion des séances passées...')
        today = date.today()
        completed_count = 0

        for cohort in cohorts:
            past_sessions = cohort.sessions.filter(date__lt=today, status='SCHEDULED')

            for session in past_sessions:
                if random.random() < 0.85:  # 85% complétées
                    session.status = 'COMPLETED'
                    session.note = random.choice([
                        "Chapitre sur les particules",
                        "Révision générale",
                        "Vocabulaire quotidien",
                        "Grammaire et exercices"
                    ])
                    session.save()
                    completed_count += 1

                    # Créer les présences
                    enrollments = cohort.enrollments.filter(is_active=True)
                    for enrollment in enrollments:
                        status = random.choice(['PRESENT', 'PRESENT', 'PRESENT', 'ABSENT', 'LATE'])
                        Attendance.objects.create(
                            session=session, student=enrollment.student,
                            enrollment=enrollment, status=status, billable=True
                        )

        self.stdout.write(self.style.SUCCESS(f'      {completed_count} séances complétées'))

    def generate_student_payments(self, admin):
        self.stdout.write('   💵 Génération des paiements étudiants...')
        payment_count = 0

        for enrollment in Enrollment.objects.all():
            total_due = float(enrollment.tariff.amount)
            amount_to_pay = total_due * random.uniform(0.4, 1.0)

            Payment.objects.create(
                enrollment=enrollment, amount=round(amount_to_pay, 2),
                method=random.choice(['CASH', 'CARD', 'CHECK']),
                date=date.today() - timedelta(days=random.randint(1, 30)),
                recorded_by=admin
            )
            payment_count += 1

        self.stdout.write(self.style.SUCCESS(f'      {payment_count} paiements créés'))

    def generate_teacher_payments(self, teachers, admin):
        self.stdout.write('   💸 Génération des paiements professeurs...')
        payment_count = 0
        today = date.today()

        # Paiement pour le mois dernier
        period_end = (today.replace(day=1) - timedelta(days=1))
        period_start = period_end.replace(day=1)

        for teacher_key in teachers:
            teacher = teachers[teacher_key]
            sessions = CourseSession.objects.filter(
                teacher=teacher, status='COMPLETED',
                date__gte=period_start, date__lte=period_end
            )

            if not sessions.exists():
                continue

            total_amount = 0
            for session in sessions:
                duration = datetime.combine(date.today(), session.end_time) - datetime.combine(date.today(), session.start_time)
                hours = duration.total_seconds() / 3600
                total_amount += hours * float(session.cohort.teacher_hourly_rate)

            if total_amount > 0:
                profile = teacher.teacher_profile
                TeacherPayment.objects.create(
                    teacher=teacher, period_start=period_start, period_end=period_end,
                    total_amount=round(total_amount, 2),
                    payment_method=profile.preferred_payment_method,
                    payment_date=period_end + timedelta(days=10),
                    recorded_by=admin,
                    notes=f"Paiement mensuel"
                )
                payment_count += 1

        self.stdout.write(self.style.SUCCESS(f'      {payment_count} paiements profs créés'))

    def print_summary(self):
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('📊 RÉSUMÉ')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Admin: username=admin, password=admin123')
        self.stdout.write(f'Professeurs: {User.objects.filter(is_teacher=True).count()}')
        self.stdout.write(f'Étudiants: {Student.objects.count()}')
        self.stdout.write(f'Groupes: {Cohort.objects.count()}')
        self.stdout.write(f'Séances totales: {CourseSession.objects.count()}')
        self.stdout.write(f'  - Complétées: {CourseSession.objects.filter(status="COMPLETED").count()}')
        self.stdout.write(f'Inscriptions: {Enrollment.objects.count()}')
        self.stdout.write(f'Paiements étudiants: {Payment.objects.count()}')
        self.stdout.write(f'Paiements professeurs: {TeacherPayment.objects.count()}')
        self.stdout.write('=' * 60)
        self.stdout.write('')