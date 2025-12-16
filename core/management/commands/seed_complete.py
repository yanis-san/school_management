from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from django.contrib.auth.hashers import make_password
import random

# Imports de tous les modèles
from core.models import User, Classroom, AcademicYear, TeacherProfile
from academics.models import Subject, Level, Cohort, WeeklySchedule, CourseSession
from finance.models import Tariff, Discount, Payment, TeacherPayment
from students.models import Student, Enrollment, Attendance


class Command(BaseCommand):
    help = "🌱 Génération complète de données réalistes pour tester TOUT le système"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('SEED COMPLET - SCHOOL MANAGEMENT SYSTEM'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # 1. Nettoyage complet
        self.clear_all_data()

        # 2. Création des données de base
        admin = self.create_admin()
        year, rooms = self.create_core_infrastructure()
        teachers = self.create_teachers_with_profiles()
        tariffs, discounts = self.create_finance_base()
        subjects, levels = self.create_academic_base()

        # 3. Création des groupes avec planning
        cohorts = self.create_cohorts_with_schedule(year, rooms, teachers, subjects, levels)

        # 4. Génération automatique des séances
        self.generate_all_sessions(cohorts)

        # 5. Création des étudiants et inscriptions
        students = self.create_students_and_enrollments(cohorts, tariffs, discounts)

        # 6. Complétion de séances passées
        self.complete_past_sessions(cohorts)

        # 7. Génération des paiements étudiants
        self.generate_student_payments(students, admin)

        # 8. Génération des paiements professeurs
        self.generate_teacher_payments(teachers, admin)

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('BASE DE DONNEES COMPLETE ET PRETE A TESTER !'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        self.print_summary(teachers, students, cohorts)

    def clear_all_data(self):
        self.stdout.write('Nettoyage complet de la base de donnees...')

        # Ordre important pour respecter les contraintes FK
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

        self.stdout.write(self.style.SUCCESS('   > Nettoyage termine\n'))

    def create_admin(self):
        self.stdout.write('Creation de l\'utilisateur admin...')
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@school.dz',
            password='admin123',
            first_name='Admin',
            last_name='System',
            phone='0550000000'
        )
        self.stdout.write(self.style.SUCCESS('   > Admin cree (username: admin, password: admin123)\n'))
        return admin

    def create_core_infrastructure(self):
        self.stdout.write('Creation de l\'infrastructure (Annee scolaire, Salles)...')

        year = AcademicYear.objects.create(
            label="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
            is_current=True
        )

        r_tokyo = Classroom.objects.create(name="Salle Tokyo", capacity=15)
        r_seoul = Classroom.objects.create(name="Salle Seoul", capacity=12)
        r_beijing = Classroom.objects.create(name="Salle Beijing", capacity=10)
        r_zoom = Classroom.objects.create(name="Zoom (En ligne)", capacity=50)

        rooms = [r_tokyo, r_seoul, r_beijing, r_zoom]

        self.stdout.write(self.style.SUCCESS(f'   > Annee scolaire : {year.label}'))
        self.stdout.write(self.style.SUCCESS(f'   > {len(rooms)} salles creees\n'))

        return year, rooms

    def create_teachers_with_profiles(self):
        self.stdout.write('Creation des professeurs avec profils financiers...')

        teachers = []

        # Professeur 1 : Yanis (Japonais)
        t_yanis = User.objects.create_user(
            username="yanis_sensei",
            email="yanis@torii.dz",
            password="password123",
            first_name="Yanis",
            last_name="Tanaka",
            is_teacher=True,
            phone="0550111111"
        )
        TeacherProfile.objects.create(
            user=t_yanis,
            preferred_payment_method='TRANSFER',
            bank_details='CCP 0021567890123',
            tax_id='199812345678901',
            notes='Professeur principal de japonais, disponible samedi et dimanche'
        )
        teachers.append(t_yanis)

        # Professeur 2 : Min-Ji (Coréen)
        t_minji = User.objects.create_user(
            username="minji_saem",
            email="minji@torii.dz",
            password="password123",
            first_name="Min-Ji",
            last_name="Kim",
            is_teacher=True,
            phone="0550222222"
        )
        TeacherProfile.objects.create(
            user=t_minji,
            preferred_payment_method='CASH',
            bank_details='',
            tax_id='199723456789012',
            notes='Préfère les cours du soir'
        )
        teachers.append(t_minji)

        # Professeur 3 : Wei (Chinois)
        t_wei = User.objects.create_user(
            username="wei_laoshi",
            email="wei@torii.dz",
            password="password123",
            first_name="Wei",
            last_name="Zhang",
            is_teacher=True,
            phone="0550333333"
        )
        TeacherProfile.objects.create(
            user=t_wei,
            preferred_payment_method='CHECK',
            bank_details='RIB 00799999001234567890123',
            tax_id='199634567890123',
            notes='Spécialiste HSK et cours intensifs'
        )
        teachers.append(t_wei)

        # Professeur 4 : Sophie (Japonais intermédiaire)
        t_sophie = User.objects.create_user(
            username="sophie_sensei",
            email="sophie@torii.dz",
            password="password123",
            first_name="Sophie",
            last_name="Dubois",
            is_teacher=True,
            phone="0550444444"
        )
        TeacherProfile.objects.create(
            user=t_sophie,
            preferred_payment_method='TRANSFER',
            bank_details='CCP 0021234567891',
            tax_id='199545678901234',
            notes='Ancienne étudiante devenue professeur'
        )
        teachers.append(t_sophie)

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(teachers)} professeurs créés avec profils financiers\n'))

        return teachers

    def create_finance_base(self):
        self.stdout.write('💰 Création des tarifs et réductions...')

        t_standard = Tariff.objects.create(name="Tarif Standard Session", amount=30000.00)
        t_etudiant = Tariff.objects.create(name="Tarif Étudiant", amount=25000.00)
        t_intensif = Tariff.objects.create(name="Cours Intensif", amount=45000.00)
        t_pack10 = Tariff.objects.create(name="Pack Privé 10h", amount=40000.00)
        t_pack20 = Tariff.objects.create(name="Pack Privé 20h", amount=75000.00)

        tariffs = [t_standard, t_etudiant, t_intensif, t_pack10, t_pack20]

        d_fratrie = Discount.objects.create(name="Réduction Fratrie", value=10, type='PERCENT', is_active=True)
        d_ancien = Discount.objects.create(name="Ancien Élève", value=5000, type='FIXED', is_active=True)
        d_ouverture = Discount.objects.create(name="Promo Ouverture", value=15, type='PERCENT', is_active=True)

        discounts = [d_fratrie, d_ancien, d_ouverture]

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(tariffs)} tarifs créés'))
        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(discounts)} réductions créées\n'))

        return tariffs, discounts

    def create_academic_base(self):
        self.stdout.write('📚 Création des matières et niveaux...')

        s_jap = Subject.objects.create(name="Japonais")
        s_kor = Subject.objects.create(name="Coréen")
        s_chi = Subject.objects.create(name="Chinois")

        l_n5 = Level.objects.create(name="N5 (Débutant)")
        l_n4 = Level.objects.create(name="N4 (Élémentaire)")
        l_topik1 = Level.objects.create(name="TOPIK 1")
        l_topik2 = Level.objects.create(name="TOPIK 2")
        l_hsk1 = Level.objects.create(name="HSK 1")
        l_hsk2 = Level.objects.create(name="HSK 2")

        subjects = [s_jap, s_kor, s_chi]
        levels = [l_n5, l_n4, l_topik1, l_topik2, l_hsk1, l_hsk2]

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(subjects)} matières créées'))
        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(levels)} niveaux créés\n'))

        return subjects, levels

    def create_cohorts_with_schedule(self, year, rooms, teachers, subjects, levels):
        self.stdout.write('🏫 Création des groupes avec planning hebdomadaire...')

        cohorts = []
        today = date.today()

        # Cohort 1 : Japonais N5 - Samedi matin
        c1 = Cohort.objects.create(
            name="Japonais N5 - Samedi Matin",
            subject=subjects[0], level=levels[0], academic_year=year,
            teacher=teachers[0], teacher_hourly_rate=1500.00,
            start_date=today - timedelta(days=60),  # Commencé il y a 2 mois
            end_date=today + timedelta(days=60),  # Se termine dans 2 mois
            standard_price=30000.00,
            schedule_generated=False  # On va le générer après
        )
        WeeklySchedule.objects.create(
            cohort=c1, day_of_week=5,  # Samedi
            start_time=time(9, 0), end_time=time(12, 0),
            classroom=rooms[0]
        )
        cohorts.append(c1)

        # Cohort 2 : Coréen TOPIK 1 - Mardi/Jeudi soir
        c2 = Cohort.objects.create(
            name="Coréen TOPIK 1 - Soir",
            subject=subjects[1], level=levels[2], academic_year=year,
            teacher=teachers[1], teacher_hourly_rate=1200.00,
            start_date=today - timedelta(days=45),
            end_date=today + timedelta(days=75),
            standard_price=25000.00,
            schedule_generated=False
        )
        WeeklySchedule.objects.create(
            cohort=c2, day_of_week=1,  # Mardi
            start_time=time(19, 0), end_time=time(20, 30),
            classroom=rooms[3]  # Zoom
        )
        WeeklySchedule.objects.create(
            cohort=c2, day_of_week=3,  # Jeudi
            start_time=time(19, 0), end_time=time(20, 30),
            classroom=rooms[3]  # Zoom
        )
        cohorts.append(c2)

        # Cohort 3 : Chinois HSK 1 - Dimanche après-midi
        c3 = Cohort.objects.create(
            name="Chinois HSK 1 - Dimanche",
            subject=subjects[2], level=levels[4], academic_year=year,
            teacher=teachers[2], teacher_hourly_rate=1800.00,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=90),
            standard_price=35000.00,
            schedule_generated=False
        )
        WeeklySchedule.objects.create(
            cohort=c3, day_of_week=6,  # Dimanche
            start_time=time(14, 0), end_time=time(17, 0),
            classroom=rooms[2]
        )
        cohorts.append(c3)

        # Cohort 4 : Japonais N4 - Samedi après-midi
        c4 = Cohort.objects.create(
            name="Japonais N4 - Samedi Après-midi",
            subject=subjects[0], level=levels[1], academic_year=year,
            teacher=teachers[3], teacher_hourly_rate=1600.00,
            start_date=today - timedelta(days=50),
            end_date=today + timedelta(days=70),
            standard_price=32000.00,
            schedule_generated=False
        )
        WeeklySchedule.objects.create(
            cohort=c4, day_of_week=5,  # Samedi
            start_time=time(14, 0), end_time=time(16, 30),
            classroom=rooms[1]
        )
        cohorts.append(c4)

        # Cohort 5 : Coréen TOPIK 2 - Lundi/Mercredi
        c5 = Cohort.objects.create(
            name="Coréen TOPIK 2 - Intensif",
            subject=subjects[1], level=levels[3], academic_year=year,
            teacher=teachers[1], teacher_hourly_rate=1400.00,
            start_date=today - timedelta(days=40),
            end_date=today + timedelta(days=80),
            standard_price=45000.00,
            schedule_generated=False
        )
        WeeklySchedule.objects.create(
            cohort=c5, day_of_week=0,  # Lundi
            start_time=time(18, 0), end_time=time(20, 0),
            classroom=rooms[1]
        )
        WeeklySchedule.objects.create(
            cohort=c5, day_of_week=2,  # Mercredi
            start_time=time(18, 0), end_time=time(20, 0),
            classroom=rooms[1]
        )
        cohorts.append(c5)

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(cohorts)} groupes créés avec planning\n'))

        return cohorts

    def generate_all_sessions(self, cohorts):
        self.stdout.write('📅 Génération automatique des séances (via Signal)...')

        total_sessions = 0
        for cohort in cohorts:
            cohort.schedule_generated = True
            cohort.save()

            sessions_count = cohort.sessions.count()
            total_sessions += sessions_count

        self.stdout.write(self.style.SUCCESS(f'   ✓ {total_sessions} séances générées automatiquement\n'))

    def create_students_and_enrollments(self, cohorts, tariffs, discounts):
        self.stdout.write('🎓 Création des étudiants et inscriptions...')

        # Noms algériens réalistes
        first_names = [
            "Amine", "Sarah", "Lina", "Mehdi", "Yasmine", "Karim", "Amira", "Riad",
            "Meriem", "Sofiane", "Nour", "Bilal", "Fatima", "Yacine", "Hanane",
            "Abdellah", "Kenza", "Nassim", "Samia", "Hichem"
        ]
        last_names = [
            "Benali", "Mokhtari", "Bouchama", "Hamdi", "Cherif", "Belaidi", "Meziane",
            "Khelifi", "Slimani", "Bouaziz", "Djebbar", "Larbi", "Mahmoudi"
        ]

        students = []
        enrollment_count = 0

        for i in range(30):  # 30 étudiants
            first = random.choice(first_names)
            last = random.choice(last_names)

            student = Student.objects.create(
                first_name=first,
                last_name=last,
                phone=f"055{str(i+1).zfill(7)}",
                phone_2=f"077{str(i+1).zfill(7)}" if random.random() > 0.5 else "",
                email=f"{first.lower()}.{last.lower()}@email.dz",
                student_code=f"2025-{str(i+1).zfill(3)}",
                motivation=random.choice([
                    "Passion pour la culture asiatique",
                    "Préparer un voyage",
                    "Évolution professionnelle",
                    "Passion pour les animes/dramas",
                    "Élargir mes horizons"
                ])
            )
            students.append(student)

            # Inscrire chaque étudiant à 1-2 groupes aléatoirement
            num_enrollments = random.randint(1, 2)
            selected_cohorts = random.sample(cohorts, num_enrollments)

            for cohort in selected_cohorts:
                # Choisir un tarif aléatoire
                tariff = random.choice(tariffs[:3])  # Standard, Étudiant, Intensif

                # Appliquer une réduction parfois
                discount = random.choice([None, None, discounts[0]]) if random.random() > 0.7 else None

                # Choisir un plan de paiement
                payment_plan = random.choice(['FULL', 'MONTHLY', 'PACK'])

                enrollment = Enrollment.objects.create(
                    student=student,
                    cohort=cohort,
                    tariff=tariff,
                    payment_plan=payment_plan,
                    hours_purchased=random.choice([10, 20]) if payment_plan == 'PACK' else 0,
                    is_active=True
                )
                enrollment_count += 1

        self.stdout.write(self.style.SUCCESS(f'   ✓ {len(students)} étudiants créés'))
        self.stdout.write(self.style.SUCCESS(f'   ✓ {enrollment_count} inscriptions créées\n'))

        return students

    def complete_past_sessions(self, cohorts):
        self.stdout.write('✅ Complétion des séances passées...')

        today = date.today()
        completed_count = 0

        for cohort in cohorts:
            # Récupérer les séances passées
            past_sessions = cohort.sessions.filter(
                date__lt=today,
                status='SCHEDULED'
            )

            for session in past_sessions:
                # Marquer comme COMPLETED (80% du temps)
                if random.random() < 0.8:
                    session.status = 'COMPLETED'
                    session.note = random.choice([
                        "Chapitre sur les particules に et で",
                        "Révision générale + quiz",
                        "Vocabulaire de la vie quotidienne",
                        "Grammaire : temps passé",
                        "Exercices de conversation",
                        "Kanji : lecture et écriture"
                    ])
                    session.save()
                    completed_count += 1

                    # Créer les présences pour cette séance
                    enrollments = cohort.enrollments.filter(is_active=True)
                    for enrollment in enrollments:
                        # 85% présent, 10% absent, 5% retard
                        rand = random.random()
                        if rand < 0.85:
                            status = 'PRESENT'
                        elif rand < 0.95:
                            status = 'ABSENT'
                        else:
                            status = 'LATE'

                        Attendance.objects.create(
                            session=session,
                            student=enrollment.student,
                            enrollment=enrollment,
                            status=status,
                            billable=True
                        )

        self.stdout.write(self.style.SUCCESS(f'   ✓ {completed_count} séances marquées comme terminées\n'))

    def generate_student_payments(self, students, admin):
        self.stdout.write('💵 Génération des paiements étudiants...')

        payment_count = 0

        for student in students:
            for enrollment in student.enrollments.all():
                # Payer une partie du montant dû
                total_due = enrollment.tariff.amount

                # Payer entre 30% et 100% du montant
                amount_to_pay = total_due * random.uniform(0.3, 1.0)

                # Créer 1 à 3 paiements
                num_payments = random.randint(1, 3)
                remaining = amount_to_pay

                for i in range(num_payments):
                    if remaining <= 0:
                        break

                    # Dernier paiement = le reste
                    if i == num_payments - 1:
                        amount = remaining
                    else:
                        amount = remaining * random.uniform(0.2, 0.6)

                    Payment.objects.create(
                        enrollment=enrollment,
                        amount=round(amount, 2),
                        method=random.choice(['CASH', 'CARD', 'CHECK']),
                        date=date.today() - timedelta(days=random.randint(1, 60)),
                        transaction_id=f"TXN{random.randint(10000, 99999)}" if random.random() > 0.5 else "",
                        recorded_by=admin
                    )
                    payment_count += 1
                    remaining -= amount

        self.stdout.write(self.style.SUCCESS(f'   ✓ {payment_count} paiements étudiants générés\n'))

    def generate_teacher_payments(self, teachers, admin):
        self.stdout.write('💸 Génération des paiements professeurs...')

        payment_count = 0
        today = date.today()

        # Créer des paiements pour les 2 derniers mois
        for month_offset in [2, 1]:
            # Période : mois dernier
            period_end = (today.replace(day=1) - timedelta(days=1))
            period_start = period_end.replace(day=1)

            # Reculer de month_offset mois
            for _ in range(month_offset - 1):
                period_end = (period_start - timedelta(days=1))
                period_start = period_end.replace(day=1)

            for teacher in teachers:
                # Calculer le montant dû
                sessions = CourseSession.objects.filter(
                    teacher=teacher,
                    status='COMPLETED',
                    date__gte=period_start,
                    date__lte=period_end
                )

                if not sessions.exists():
                    continue

                total_hours = 0
                total_amount = 0

                for session in sessions:
                    duration = datetime.combine(date.today(), session.end_time) - datetime.combine(date.today(), session.start_time)
                    hours = duration.total_seconds() / 3600
                    pay = hours * float(session.cohort.teacher_hourly_rate)

                    total_hours += hours
                    total_amount += pay

                if total_amount > 0:
                    # Créer le paiement
                    profile = teacher.teacher_profile

                    TeacherPayment.objects.create(
                        teacher=teacher,
                        period_start=period_start,
                        period_end=period_end,
                        total_amount=round(total_amount, 2),
                        payment_method=profile.preferred_payment_method,
                        payment_date=period_end + timedelta(days=random.randint(5, 15)),
                        recorded_by=admin,
                        proof_reference=f"PAY{random.randint(1000, 9999)}" if profile.preferred_payment_method != 'CASH' else "",
                        notes=f"Paiement pour {round(total_hours, 2)}h de cours"
                    )
                    payment_count += 1

        self.stdout.write(self.style.SUCCESS(f'   ✓ {payment_count} paiements professeurs générés\n'))

    def print_summary(self, teachers, students, cohorts):
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ DES DONNÉES GÉNÉRÉES'))
        self.stdout.write('='*70 + '\n')

        self.stdout.write(f'👤 Admin : username=admin, password=admin123')
        self.stdout.write(f'👨‍🏫 Professeurs : {len(teachers)} (avec profils financiers)')
        self.stdout.write(f'🎓 Étudiants : {len(students)}')
        self.stdout.write(f'🏫 Groupes/Classes : {len(cohorts)}')
        self.stdout.write(f'📅 Séances totales : {CourseSession.objects.count()}')
        self.stdout.write(f'   ✓ Complétées : {CourseSession.objects.filter(status="COMPLETED").count()}')
        self.stdout.write(f'   ✓ À venir : {CourseSession.objects.filter(status="SCHEDULED", date__gte=date.today()).count()}')
        self.stdout.write(f'📝 Inscriptions : {Enrollment.objects.count()}')
        self.stdout.write(f'💵 Paiements étudiants : {Payment.objects.count()}')
        self.stdout.write(f'💸 Paiements professeurs : {TeacherPayment.objects.count()}')

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('🚀 VOUS POUVEZ MAINTENANT TESTER TOUT LE SYSTÈME !'))
        self.stdout.write('='*70 + '\n')
