# documents/views.py
from datetime import datetime
from io import BytesIO
import zipfile

from django.conf import settings
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from .sync import SyncManager
from django.shortcuts import get_object_or_404, render

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from academics.models import Cohort, CourseSession
from core.models import AcademicYear
from finance.models import Payment, TeacherCohortPayment
from students.models import Enrollment, Student, Attendance


def _logo_path():
    """Retourne le chemin absolu du logo s'il existe."""
    candidate = settings.BASE_DIR / 'static' / 'images' / 'logo_horizontal.png'
    return candidate if candidate.exists() else None


def _header_footer_maker(title: str):
    """Construit un dessinateur header/footer uniforme pour les PDFs."""
    generated = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    logo = _logo_path()

    def _draw(canvas_obj, doc):
        width, height = doc.pagesize
        canvas_obj.setStrokeColor(colors.lightgrey)
        canvas_obj.setLineWidth(0.5)

        # Header
        y_header = height - 1.5 * cm
        canvas_obj.line(1.5 * cm, y_header + 0.4 * cm, width - 1.5 * cm, y_header + 0.4 * cm)
        if logo:
            canvas_obj.drawImage(str(logo), 1.5 * cm, height - 2.5 * cm, width=3.5 * cm, preserveAspectRatio=True, mask='auto')
        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.drawString(5.2 * cm, height - 2.0 * cm, f"{title}")

        # Footer
        canvas_obj.line(1.5 * cm, 1.6 * cm, width - 1.5 * cm, 1.6 * cm)
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawString(1.5 * cm, 1.2 * cm, "Institut Torii - Généré automatiquement")
        canvas_obj.drawRightString(width - 1.5 * cm, 1.2 * cm, f"Généré le {generated}")

    return _draw


def _build_pdf_response(filename: str, title: str, story_builder, pagesize=A4):
    """Construit une réponse PDF via reportlab et ajoute header/footer uniformes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=3 * cm,
        bottomMargin=2.2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []
    story_builder(story, styles)

    header_footer = _header_footer_maker(title)
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    # Encoder le filename pour supporter les caractères spéciaux et accents
    from urllib.parse import quote
    encoded_filename = quote(filename)
    response['Content-Disposition'] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
    return response


@login_required
def select_cohort(request):
    """Vue principale qui propose les exports PDF globaux et par groupe."""
    cohorts = Cohort.objects.select_related('teacher', 'subject', 'academic_year').order_by('-academic_year__start_date', 'name')
    current_year = AcademicYear.get_current()
    return render(request, 'documents/select_cohort.html', {
        'cohorts': cohorts,
        'current_year': current_year,
    })


@login_required
def global_reports(request):
    """Rapport global PDF (année académique courante) : étudiants, encaissements, paiements profs."""
    current_year = AcademicYear.get_current()
    if not current_year:
        return HttpResponse("Aucune année académique active (is_current=True).", status=400)

    enrollments = (
        Enrollment.objects.filter(cohort__academic_year=current_year)
        .select_related('student', 'cohort', 'tariff')
        .prefetch_related('payments')
        .order_by('student__last_name', 'student__first_name')
    )

    payments = (
        Payment.objects.filter(enrollment__cohort__academic_year=current_year)
        .select_related('enrollment__student', 'enrollment__cohort')
        .order_by('-date')
    )

    teacher_payments = (
        TeacherCohortPayment.objects.filter(cohort__academic_year=current_year)
        .select_related('teacher', 'cohort')
        .order_by('-payment_date')
    )

    def build_story(story, styles):
        h1 = styles['Heading1']
        h2 = styles['Heading2']

        story.append(Paragraph(f"Rapports globaux – {current_year.label}", h1))
        story.append(Spacer(1, 0.3 * cm))

        # Étudiants
        story.append(Paragraph("Étudiants (année courante)", h2))
        data = [["Code", "Nom", "Téléphone", "Email", "Cohorts", "Tarif", "Payé", "Reste"]]
        student_rows = []
        for enr in enrollments:
            total_paid = enr.payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
            balance = enr.tariff.amount - total_paid
            student_rows.append([
                enr.student.student_code or "—",
                f"{enr.student.last_name} {enr.student.first_name}",
                enr.student.phone or "—",
                enr.student.email or "—",
                enr.cohort.name,
                f"{enr.tariff.amount:,} DA".replace(',', ' '),
                f"{total_paid:,} DA".replace(',', ' '),
                f"{balance:,} DA".replace(',', ' '),
            ])
        data.extend(student_rows[:500])  # éviter des PDFs gigantesques
        story.append(Table(data, repeatRows=1, hAlign='LEFT', colWidths=[2.2*cm,4*cm,3*cm,3.5*cm,4*cm,2.5*cm,2.5*cm,2.5*cm], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (5,1), (-1,-1), 'RIGHT'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(Spacer(1, 0.4 * cm))

        # Encaissements caisse
        story.append(Paragraph("Encaissements (caisse)", h2))
        pay_data = [["Date", "Étudiant", "Cohort", "Montant", "Méthode", "Reçu par"]]
        for p in payments[:300]:
            student = p.enrollment.student
            cohort_obj = p.enrollment.cohort
            receiver_name = "—"
            if getattr(p, "recorded_by", None):
                receiver_name = (
                    p.recorded_by.get_full_name()
                    if hasattr(p.recorded_by, "get_full_name")
                    else getattr(p.recorded_by, "username", "—")
                )
            method_display = (
                p.get_method_display() if hasattr(p, "get_method_display")
                else (p.get_payment_method_display() if hasattr(p, "get_payment_method_display") else "—")
            )
            pay_data.append([
                p.date.strftime('%d/%m/%Y'),
                f"{student.last_name} {student.first_name}",
                cohort_obj.name,
                f"{p.amount:,} DA".replace(',', ' '),
                method_display,
                receiver_name,
            ])
        story.append(Table(pay_data, repeatRows=1, hAlign='LEFT', colWidths=[2.2*cm,4.5*cm,4*cm,2.5*cm,3*cm,3.5*cm], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (3,1), (3,-1), 'RIGHT'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(Spacer(1, 0.4 * cm))

        # Paiements profs par cohort
        story.append(Paragraph("Paiements professeurs (par cohort)", h2))
        tp_data = [["Date Paiement", "Professeur", "Cohort", "Période", "Dû", "Payé", "Méthode"]]
        for tp in teacher_payments[:300]:
            tp_data.append([
                tp.payment_date.strftime('%d/%m/%Y'),
                tp.teacher.get_full_name(),
                tp.cohort.name,
                f"{tp.period_start.strftime('%d/%m/%Y')} → {tp.period_end.strftime('%d/%m/%Y')}",
                f"{tp.amount_due:,} DA".replace(',', ' '),
                f"{tp.amount_paid:,} DA".replace(',', ' '),
                tp.get_payment_method_display(),
            ])
        story.append(Table(tp_data, repeatRows=1, hAlign='LEFT', colWidths=[2.5*cm,4*cm,4*cm,4*cm,2.5*cm,2.5*cm,2.5*cm], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (4,1), (5,-1), 'RIGHT'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))

    filename = f"Rapports_Globaux_{current_year.label}.pdf"
    return _build_pdf_response(filename, f"Rapports globaux {current_year.label}", build_story, pagesize=landscape(A4))


@login_required
def cohort_report(request, cohort_id):
    """Rapport PDF détaillé pour un cohort : fiche, étudiants (paiements), paie prof."""
    cohort = get_object_or_404(Cohort.objects.select_related('teacher', 'subject', 'level', 'academic_year'), id=cohort_id)

    enrollments = (
        cohort.enrollments.select_related('student', 'tariff')
        .prefetch_related('payments')
        .order_by('student__last_name', 'student__first_name')
    )

    cohort_tp = TeacherCohortPayment.objects.filter(cohort=cohort).select_related('teacher').order_by('-payment_date')

    sessions = cohort.sessions.all()
    # Calcul en Decimal pour éviter les mélanges float/Decimal
    due_amount = sum((Decimal(sess.actual_minutes) / Decimal(60)) * Decimal(sess.pay_hourly_rate) for sess in sessions)

    paid_amount = cohort_tp.aggregate(total=Coalesce(Sum('amount_paid'), Value(0), output_field=DecimalField(max_digits=10, decimal_places=2)))['total']

    def build_story(story, styles):
        h1 = styles['Heading1']
        h2 = styles['Heading2']

        story.append(Paragraph(f"Cohort : {cohort.name}", h1))
        story.append(Spacer(1, 0.3 * cm))

        # Fiche synthèse
        story.append(Paragraph("Fiche synthèse", h2))
        meta_data = [
            ["Matière", cohort.subject.name],
            ["Niveau", cohort.level.name],
            ["Modalité", cohort.get_modality_display()],
            ["Individuel", "Oui" if cohort.is_individual else "Non"],
            ["Professeur", cohort.teacher.get_full_name()],
            ["Suppléants", ', '.join(t.get_full_name() for t in cohort.substitute_teachers.all()) or "—"],
            ["Période", f"{cohort.start_date.strftime('%d/%m/%Y')} → {cohort.end_date.strftime('%d/%m/%Y')}"],
            ["Salle(s)", ', '.join(sorted({s.classroom.name for s in sessions if s.classroom})) or "—"],
            ["Tarif horaire", f"{cohort.teacher_hourly_rate:,} DA/h".replace(',', ' ')],
            ["Prix standard", f"{cohort.standard_price:,} DA".replace(',', ' ')],
        ]
        story.append(Table(meta_data, hAlign='LEFT', colWidths=[4*cm, 12*cm], style=[
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(Spacer(1, 0.4 * cm))

        # Étudiants
        story.append(Paragraph("Étudiants et paiements", h2))
        student_data = [["Code", "Nom", "Téléphone", "Email", "Tarif", "Payé", "Reste"]]
        for enr in enrollments:
            total_paid = enr.payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
            balance = enr.tariff.amount - total_paid
            student_data.append([
                enr.student.student_code or "—",
                f"{enr.student.last_name} {enr.student.first_name}",
                enr.student.phone or "—",
                enr.student.email or "—",
                f"{enr.tariff.amount:,} DA".replace(',', ' '),
                f"{total_paid:,} DA".replace(',', ' '),
                f"{balance:,} DA".replace(',', ' '),
            ])
        story.append(Table(student_data, repeatRows=1, hAlign='LEFT', colWidths=[2.2*cm,4.5*cm,3*cm,3.5*cm,2.5*cm,2.5*cm,2.5*cm], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (4,1), (-1,-1), 'RIGHT'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(Spacer(1, 0.4 * cm))

        # Paie professeur pour ce cohort
        story.append(Paragraph("Paie professeur (cohort)", h2))
        resume_data = [
            ["Séances (totales)", str(sessions.count())],
            ["Montant dû estimé", f"{due_amount:,.0f} DA".replace(',', ' ')],
            ["Déjà payé", f"{paid_amount:,.0f} DA".replace(',', ' ')],
            ["Reste à payer", f"{(due_amount - paid_amount):,.0f} DA".replace(',', ' ')],
        ]
        story.append(Table(resume_data, hAlign='LEFT', colWidths=[5*cm, 11*cm], style=[
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(Spacer(1, 0.3 * cm))

        tp_table = [["Date", "Période", "Payé", "Méthode", "Référence/Notes"]]
        for tp in cohort_tp:
            tp_table.append([
                tp.payment_date.strftime('%d/%m/%Y'),
                f"{tp.period_start.strftime('%d/%m/%Y')} → {tp.period_end.strftime('%d/%m/%Y')}",
                f"{tp.amount_paid:,} DA".replace(',', ' '),
                tp.get_payment_method_display(),
                tp.notes or tp.proof_reference or "—",
            ])
        story.append(Table(tp_table, repeatRows=1, hAlign='LEFT', colWidths=[2.5*cm,4*cm,2.5*cm,2.5*cm,6.5*cm], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))

    filename = f"Cohort_{cohort.name.replace(' ', '_')}.pdf"
    return _build_pdf_response(filename, f"Cohort {cohort.name}", build_story, pagesize=landscape(A4))


@login_required
def download_cohort_attendance(request, cohort_id):
    """Liste de présence (statuts) en PDF pour un cohort."""
    cohort = get_object_or_404(Cohort, id=cohort_id)
    enrollments = cohort.enrollments.select_related('student').order_by('student__last_name')
    sessions = cohort.sessions.order_by('date', 'start_time')

    from students.models import Attendance
    attendance_dict = {
        (att.student_id, att.session_id): att.status
        for att in Attendance.objects.filter(session__cohort=cohort).select_related('session', 'student')
    }

    STATUS_SYMBOLS = {
        'PRESENT': '✓',
        'ABSENT': '✗',
        'LATE': '⌚',
        'EXCUSED': 'E',
    }

    def build_story(story, styles):
        h1 = styles['Heading1']
        normal = styles['BodyText']
        story.append(Paragraph(f"Présence – {cohort.name}", h1))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"Professeur : {cohort.teacher.get_full_name()}", normal))
        story.append(Paragraph(f"Période : {cohort.start_date.strftime('%d/%m/%Y')} → {cohort.end_date.strftime('%d/%m/%Y')}", normal))
        story.append(Spacer(1, 0.3 * cm))

        data = [["N°", "Étudiant"] + [s.date.strftime('%d/%m') for s in sessions]]
        for idx, enr in enumerate(enrollments, 1):
            row = [idx, f"{enr.student.last_name} {enr.student.first_name}"]
            for s in sessions:
                status = attendance_dict.get((enr.student_id, s.id), 'PRESENT')
                row.append(STATUS_SYMBOLS.get(status, '?'))
            data.append(row)

        table = Table(data, repeatRows=1, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('ALIGN', (2,1), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("Légende : ✓ Présent | ✗ Absent | ⌚ Retard | E Excusé", normal))

    filename = f"Presence_{cohort.name.replace(' ', '_')}.pdf"
    return _build_pdf_response(filename, f"Présence {cohort.name}", build_story, pagesize=landscape(A4))


@login_required
def download_session_attendance(request, session_id):
    """Liste de présence pour une séance (PDF)."""
    session = get_object_or_404(CourseSession.objects.select_related('cohort', 'teacher'), id=session_id)
    enrollments = session.cohort.enrollments.select_related('student').order_by('student__last_name')

    from students.models import Attendance
    att = {
        a.student_id: a.status for a in Attendance.objects.filter(session=session).select_related('student')
    }
    STATUS_LABELS = {
        'PRESENT': 'Présent',
        'ABSENT': 'Absent',
        'LATE': 'En Retard',
        'EXCUSED': 'Excusé',
    }

    def build_story(story, styles):
        h1 = styles['Heading1']
        normal = styles['BodyText']
        story.append(Paragraph(f"Présence – {session.cohort.name}", h1))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"Date : {session.date.strftime('%d/%m/%Y')} | Horaire : {session.display_start_time.strftime('%H:%M')} – {session.display_end_time.strftime('%H:%M')}", normal))
        story.append(Paragraph(f"Professeur : {session.teacher.get_full_name()}", normal))
        story.append(Spacer(1, 0.3 * cm))

        data = [["N°", "Étudiant", "Statut", "Signature"]]
        for idx, enr in enumerate(enrollments, 1):
            # Par défaut "Présent" pour la feuille d'émargement, sauf si un statut est déjà enregistré
            status_display = STATUS_LABELS.get(att.get(enr.student_id, 'PRESENT'), 'Présent')
            data.append([idx, f"{enr.student.last_name} {enr.student.first_name}", status_display, ""])

        table = Table(data, repeatRows=1, hAlign='LEFT', colWidths=[1.2*cm,7*cm,4*cm,5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(table)

    filename = f"Presence_{session.cohort.name.replace(' ', '_')}_{session.date.strftime('%Y%m%d')}.pdf"
    return _build_pdf_response(filename, f"Présence {session.cohort.name}", build_story)


def _generate_pdf_bytes(title: str, build_story, pagesize=None):
    """Helper : génère les bytes PDF sans réponse HTTP.
    pagesize: override page size (default landscape A4)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(pagesize or landscape(A4)),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=3 * cm,
        bottomMargin=2.2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []
    build_story(story, styles)

    header_footer = _header_footer_maker(title)
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

    buffer.seek(0)
    return buffer.read()


@login_required
def download_cohort_zip(request, cohort_id):
    """ZIP d'un cohort : contient rapport + présences."""
    cohort = get_object_or_404(Cohort.objects.select_related('teacher', 'subject', 'level', 'academic_year'), id=cohort_id)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Rapport cohort
        enrollments = (
            cohort.enrollments.select_related('student', 'tariff')
            .prefetch_related('payments')
            .order_by('student__last_name', 'student__first_name')
        )
        cohort_tp = TeacherCohortPayment.objects.filter(cohort=cohort).select_related('teacher').order_by('-payment_date')
        sessions = cohort.sessions.all()
        # Calcul en Decimal pour éviter les mélanges float/Decimal
        due_amount = sum((Decimal(sess.actual_minutes) / Decimal(60)) * Decimal(sess.pay_hourly_rate) for sess in sessions)
        paid_amount = cohort_tp.aggregate(total=Coalesce(Sum('amount_paid'), Value(0), output_field=DecimalField(max_digits=10, decimal_places=2)))['total']

        def build_cohort_story(story, styles):
            h1 = styles['Heading1']
            h2 = styles['Heading2']
            story.append(Paragraph(f"Cohort : {cohort.name}", h1))
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Fiche synthèse", h2))
            meta_data = [
                ["Matière", cohort.subject.name],
                ["Niveau", cohort.level.name],
                ["Modalité", cohort.get_modality_display()],
                ["Professeur", cohort.teacher.get_full_name()],
                ["Période", f"{cohort.start_date.strftime('%d/%m/%Y')} → {cohort.end_date.strftime('%d/%m/%Y')}"],
                ["Tarif horaire", f"{cohort.teacher_hourly_rate:,} DA/h".replace(',', ' ')],
            ]
            story.append(Table(meta_data, hAlign='LEFT', colWidths=[4*cm, 12*cm], style=[
                ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ]))
            story.append(Spacer(1, 0.4 * cm))

            story.append(Paragraph("Étudiants et paiements", h2))
            student_data = [["Code", "Nom", "Tarif", "Payé", "Reste"]]
            for enr in enrollments:
                total_paid = enr.payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
                balance = enr.tariff.amount - total_paid
                student_data.append([
                    enr.student.student_code or "—",
                    f"{enr.student.last_name} {enr.student.first_name}",
                    f"{enr.tariff.amount:,} DA".replace(',', ' '),
                    f"{total_paid:,} DA".replace(',', ' '),
                    f"{balance:,} DA".replace(',', ' '),
                ])
            story.append(Table(student_data, repeatRows=1, hAlign='LEFT', colWidths=[2.2*cm,5*cm,2.5*cm,2.5*cm,2.5*cm], style=[
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ]))

        report_pdf = _generate_pdf_bytes(f"Cohort {cohort.name}", build_cohort_story)
        zf.writestr(f"{cohort.name.replace(' ', '_')}/01_Rapport_Complet.pdf", report_pdf)

        # Présences cohort
        from students.models import Attendance
        enrollments_att = cohort.enrollments.select_related('student').order_by('student__last_name')
        sessions_att = cohort.sessions.order_by('date', 'start_time')
        attendance_dict = {
            (att.student_id, att.session_id): att.status
            for att in Attendance.objects.filter(session__cohort=cohort)
        }

        def build_att_story(story, styles):
            h1 = styles['Heading1']
            normal = styles['BodyText']
            story.append(Paragraph(f"Présence – {cohort.name}", h1))
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(f"Professeur : {cohort.teacher.get_full_name()}", normal))
            story.append(Spacer(1, 0.3 * cm))

            STATUS_SYMBOLS = {'PRESENT': '✓', 'ABSENT': '✗', 'LATE': '⌚', 'EXCUSED': 'E'}
            data = [["N°", "Étudiant"] + [s.date.strftime('%d/%m') for s in sessions_att]]
            for idx, enr in enumerate(enrollments_att, 1):
                row = [idx, f"{enr.student.last_name} {enr.student.first_name}"]
                for s in sessions_att:
                    status = attendance_dict.get((enr.student_id, s.id), 'PRESENT')
                    row.append(STATUS_SYMBOLS.get(status, '?'))
                data.append(row)

            table = Table(data, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('ALIGN', (2,1), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph("Légende : ✓ Présent | ✗ Absent | ⌚ Retard | E Excusé", normal))

        att_pdf = _generate_pdf_bytes(f"Présence {cohort.name}", build_att_story)
        zf.writestr(f"{cohort.name.replace(' ', '_')}/02_Presences.pdf", att_pdf)

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="Cohort_{cohort.name.replace(" ", "_")}.zip"'
    return response


@login_required
def download_all_cohorts_zip(request):
    """ZIP global institut : tous les cohorts + rapport global organisés par année."""
    current_year = AcademicYear.get_current()
    if not current_year:
        return HttpResponse("Aucune année académique active (is_current=True).", status=400)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Rapport global
        enrollments = (
            Enrollment.objects.filter(cohort__academic_year=current_year)
            .select_related('student', 'cohort', 'tariff')
            .prefetch_related('payments')
            .order_by('student__last_name', 'student__first_name')
        )
        payments = (
            Payment.objects.filter(enrollment__cohort__academic_year=current_year)
            .select_related('enrollment__student', 'enrollment__cohort')
            .order_by('-date')
        )
        teacher_payments = (
            TeacherCohortPayment.objects.filter(cohort__academic_year=current_year)
            .select_related('teacher', 'cohort')
            .order_by('-payment_date')
        )

        def build_global_story(story, styles):
            h1 = styles['Heading1']
            h2 = styles['Heading2']
            story.append(Paragraph(f"Rapports globaux – {current_year.label}", h1))
            story.append(Spacer(1, 0.3 * cm))

            story.append(Paragraph("Étudiants (année courante)", h2))
            data = [["Code", "Nom", "Cohort", "Tarif", "Payé", "Reste"]]
            for enr in enrollments[:300]:
                total_paid = enr.payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
                balance = enr.tariff.amount - total_paid
                data.append([
                    enr.student.student_code or "—",
                    f"{enr.student.last_name} {enr.student.first_name}",
                    enr.cohort.name,
                    f"{enr.tariff.amount:,}".replace(',', ' '),
                    f"{total_paid:,}".replace(',', ' '),
                    f"{balance:,}".replace(',', ' '),
                ])
            story.append(Table(data, repeatRows=1, hAlign='LEFT', colWidths=[2*cm,4*cm,4*cm,2.2*cm,2.2*cm,2.2*cm], style=[
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('FONTSIZE', (0,1), (-1,-1), 7),
                ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ]))
            story.append(Spacer(1, 0.3 * cm))

            story.append(Paragraph("Encaissements", h2))
            pay_data = [["Date", "Étudiant", "Montant"]]
            for pay in payments[:150]:
                pay_data.append([
                    pay.date.strftime('%d/%m/%Y'),
                    f"{pay.enrollment.student.last_name} {pay.enrollment.student.first_name}",
                    f"{pay.amount:,}".replace(',', ' '),
                ])
            story.append(Table(pay_data, repeatRows=1, hAlign='LEFT', colWidths=[2.5*cm,6*cm,2.5*cm], style=[
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('FONTSIZE', (0,1), (-1,-1), 7),
                ('ALIGN', (2,1), (2,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ]))

        global_pdf = _generate_pdf_bytes(f"Rapports globaux {current_year.label}", build_global_story)
        zf.writestr(f"00_INSTITUT_{current_year.label}/00_Rapport_Global.pdf", global_pdf)

        # Tous les cohorts
        cohorts = Cohort.objects.filter(academic_year=current_year).select_related('teacher', 'subject', 'level')
        for cohort in cohorts:
            cohort_name = cohort.name.replace(' ', '_')
            folder = f"00_INSTITUT_{current_year.label}/{cohort_name}/"

            # Rapport cohort
            enrollments_c = (
                cohort.enrollments.select_related('student', 'tariff')
                .prefetch_related('payments')
                .order_by('student__last_name')
            )
            cohort_tp = TeacherCohortPayment.objects.filter(cohort=cohort).order_by('-payment_date')
            sessions_c = cohort.sessions.all()
            due = sum((s.actual_minutes / 60.0) * s.pay_hourly_rate for s in sessions_c)
            paid = cohort_tp.aggregate(total=Coalesce(Sum('amount_paid'), Value(0), output_field=DecimalField(max_digits=10, decimal_places=2)))['total']

            def build_c_story(story, styles):
                h1 = styles['Heading1']
                h2 = styles['Heading2']
                story.append(Paragraph(f"Cohort : {cohort.name}", h1))
                story.append(Spacer(1, 0.2 * cm))
                story.append(Paragraph("Fiche", h2))
                meta = [
                    ["Matière", cohort.subject.name],
                    ["Niveau", cohort.level.name if cohort.level else "—"],
                    ["Profs", cohort.teacher.get_full_name()],
                ]
                story.append(Table(meta, hAlign='LEFT', colWidths=[3*cm, 10*cm], style=[
                    ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
                    ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ]))
                story.append(Spacer(1, 0.2 * cm))

                story.append(Paragraph("Étudiants", h2))
                std = [["Code", "Nom", "Tarif", "Payé"]]
                for enr in enrollments_c[:100]:
                    total_p = enr.payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
                    std.append([
                        enr.student.student_code or "—",
                        f"{enr.student.last_name}",
                        f"{enr.tariff.amount:,}".replace(',', ' '),
                        f"{total_p:,}".replace(',', ' '),
                    ])
                story.append(Table(std, repeatRows=1, hAlign='LEFT', colWidths=[2*cm,5*cm,2.2*cm,2.2*cm], style=[
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 8),
                    ('FONTSIZE', (0,1), (-1,-1), 7),
                    ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ]))

            cohort_pdf = _generate_pdf_bytes(f"Cohort {cohort.name}", build_c_story)
            zf.writestr(f"{folder}01_Rapport.pdf", cohort_pdf)

            # Présences cohort
            from students.models import Attendance
            enr_att = cohort.enrollments.select_related('student').order_by('student__last_name')
            sess_att = cohort.sessions.order_by('date')
            att_d = {
                (a.student_id, a.session_id): a.status
                for a in Attendance.objects.filter(session__cohort=cohort)
            }

            def build_att2(story, styles):
                h1 = styles['Heading1']
                story.append(Paragraph(f"Présence – {cohort.name}", h1))
                story.append(Spacer(1, 0.2 * cm))
                STATUS_SYMBOLS = {'PRESENT': '✓', 'ABSENT': '✗', 'LATE': '⌚', 'EXCUSED': 'E'}
                data = [["N°", "Étudiant"] + [s.date.strftime('%d/%m') for s in sess_att[:20]]]
                for idx, enr in enumerate(enr_att, 1):
                    row = [idx, f"{enr.student.last_name}"]
                    for s in sess_att[:20]:
                        row.append(STATUS_SYMBOLS.get(att_d.get((enr.student_id, s.id), 'PRESENT'), '?'))
                    data.append(row)
                table = Table(data, repeatRows=1, hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 7),
                    ('FONTSIZE', (0,1), (-1,-1), 6),
                    ('ALIGN', (0,1), (-1,-1), 'CENTER'),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ]))
                story.append(table)

            att2_pdf = _generate_pdf_bytes(f"Présence {cohort.name}", build_att2)
            zf.writestr(f"{folder}02_Presences.pdf", att2_pdf)

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="Institut_{current_year.label}_{datetime.now().strftime("%Y%m%d")}.zip"'
    return response


# ============ SYNCHRONISATION ============

@login_required
@require_http_methods(["GET"])
def export_sync_csv(request, cohort_id, data_type='attendance'):
    """
    Exporte un CSV de sync (presences ou paiements).
    Le prof télécharge ce fichier, le modifie hors-ligne, puis le réupload.
    """
    cohort = get_object_or_404(Cohort, id=cohort_id)
    
    if data_type == 'attendance':
        csv_content = SyncManager.export_attendance_sync_csv(cohort_id)
        filename = f"SYNC_Presences_{cohort.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    elif data_type == 'payments':
        csv_content = SyncManager.export_payments_sync_csv(cohort_id)
        filename = f"SYNC_Paiements_{cohort.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        return HttpResponse("Type de données invalide.", status=400)
    
    response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_http_methods(["POST"])
def import_sync_csv(request, cohort_id, data_type='attendance'):
    """
    Importe et merge un CSV de sync.
    Résout les conflits automatiquement par timestamps.
    """
    if 'sync_file' not in request.FILES:
        return HttpResponse("Pas de fichier reçu.", status=400)
    
    uploaded_file = request.FILES['sync_file']
    csv_content = uploaded_file.read().decode('utf-8')
    
    try:
        if data_type == 'attendance':
            changes = SyncManager.import_attendance_sync_csv(csv_content, request.user)
        elif data_type == 'payments':
            changes = SyncManager.import_payments_sync_csv(csv_content, request.user)
        else:
            return HttpResponse("Type de données invalide.", status=400)
        
        # Retour JSON avec résumé du merge
        import json
        response_data = {
            'status': 'success',
            'message': f"Synchronisation complète : {changes['created']} créés, {changes['updated']} mis à jour, {changes.get('conflicts', 0)} conflits résolus.",
            'changes': changes,
        }
        return HttpResponse(json.dumps(response_data), content_type='application/json')
    
    except Exception as e:
        return HttpResponse(f"Erreur lors du merge : {str(e)}", status=500)


@login_required
def sync_page(request):
    """Page dédiée à la synchronisation globale"""
    return render(request, 'documents/sync_page.html')


@login_required
def sync_history(request):
    """Historique des synchronisations"""
    from .models import SyncLog
    logs = SyncLog.objects.all()[:20]  # Derniers 20 imports
    return render(request, 'documents/sync_history.html', {'logs': logs})


@login_required
def sync_detail(request, sync_id):
    """Détails d'une synchronisation"""
    from .models import SyncLog
    try:
        log = SyncLog.objects.get(id=sync_id)
    except SyncLog.DoesNotExist:
        return HttpResponse("Synchronisation non trouvée", status=404)
    
    return render(request, 'documents/sync_detail.html', {'log': log})


@login_required
def export_global_sync(request):
    """
    Exporte UN SEUL fichier ZIP contenant TOUTES les données de sync:
    - presences.csv (toutes les présences de tous les cohortes)
    - paiements.csv (tous les paiements de tous les cohortes)
    """
    from .sync import GlobalSyncManager
    
    zip_buffer, filename = GlobalSyncManager.export_global_sync_zip()
    
    if not zip_buffer:
        return HttpResponse("Aucune année académique courante trouvée.", status=404)
    
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_http_methods(["POST"])
def import_global_sync(request):
    """
    Importe et synchronise TOUTES les données depuis un ZIP global.
    Résout les conflits automatiquement par timestamps (last-write-wins).
    SAUVEGARDE AUTOMATIQUE avant import.
    """
    import json
    from .sync import GlobalSyncManager
    from .models import SyncLog
    
    if 'sync_file' not in request.FILES:
        return HttpResponse(json.dumps({
            'status': 'error',
            'message': 'Aucun fichier reçu.'
        }), content_type='application/json', status=400)
    
    uploaded_file = request.FILES['sync_file']
    
    try:
        stats = GlobalSyncManager.import_global_sync_zip(uploaded_file)
        
        # Créer le SyncLog
        sync_log = SyncLog.objects.create(
            user=request.user,
            backup_created=stats['backup_created'],
            backup_path=stats.get('backup_path', ''),
            backup_message=stats.get('backup_message', ''),
            stats_json=stats,
            error_count=len(stats.get('errors', [])),
            errors_json=stats.get('errors', [])
        )
        
        return HttpResponse(json.dumps({
            'success': True,
            'sync_log_id': sync_log.id,
            'backup_created': stats['backup_created'],
            'backup_path': stats.get('backup_path', ''),
            'backup_message': stats.get('backup_message', ''),
            'subjects_added': stats['subjects_added'],
            'subjects_updated': stats['subjects_updated'],
            'levels_added': stats['levels_added'],
            'levels_updated': stats['levels_updated'],
            'tariffs_added': stats['tariffs_added'],
            'tariffs_updated': stats['tariffs_updated'],
            'discounts_added': stats['discounts_added'],
            'discounts_updated': stats['discounts_updated'],
            'students_added': stats['students_added'],
            'students_updated': stats['students_updated'],
            'cohorts_added': stats['cohorts_added'],
            'cohorts_updated': stats['cohorts_updated'],
            'sessions_added': stats['sessions_added'],
            'sessions_updated': stats['sessions_updated'],
            'sessions_deleted': stats.get('sessions_deleted', 0),
            'enrollments_added': stats['enrollments_added'],
            'enrollments_updated': stats['enrollments_updated'],
            'enrollments_deleted': stats.get('enrollments_deleted', 0),
            'presences_added': stats['presences_added'],
            'presences_updated': stats['presences_updated'],
            'paiements_etudiants_added': stats['paiements_etudiants_added'],
            'paiements_etudiants_updated': stats['paiements_etudiants_updated'],
            'paiements_profs_added': stats['paiements_profs_added'],
            'paiements_profs_updated': stats['paiements_profs_updated'],
            'errors': stats['errors']
        }), content_type='application/json')
    
    except Exception as e:
        return HttpResponse(json.dumps({
            'success': False,
            'error': str(e)
        }), content_type='application/json', status=500)


@login_required
def download_student_complete_pdf(request, student_id):
    """Dossier complet d'un étudiant en UN SEUL PDF avec TOUTES les informations."""
    student = get_object_or_404(Student, id=student_id)
    
    # Récupérer toutes les données
    enrollments = Enrollment.objects.filter(student=student).select_related(
        'cohort', 'cohort__subject', 'cohort__level', 'cohort__academic_year', 'tariff'
    ).prefetch_related('payments').order_by('-cohort__start_date')
    
    all_payments = Payment.objects.filter(enrollment__student=student).select_related(
        'enrollment', 'enrollment__cohort'
    ).order_by('-date')
    
    all_attendances = Attendance.objects.filter(student=student).select_related(
        'session', 'session__cohort', 'enrollment'
    ).order_by('-session__date')
    
    absences = all_attendances.filter(status='ABSENT')
    
    def build_story(story, styles):
        h1 = styles['Heading1']
        h2 = styles['Heading2']
        normal = styles['BodyText']
        
        # Page 1: Informations personnelles
        story.append(Paragraph(f"DOSSIER COMPLET - {student.last_name} {student.first_name}", h1))
        story.append(Spacer(1, 0.5 * cm))
        
        info_data = [
            ["Code Étudiant", student.student_code or "—"],
            ["Nom complet", f"{student.last_name} {student.first_name}"],
            ["Sexe", student.get_sex_display() if student.sex else "—"],
            ["Date de naissance", student.birth_date.strftime('%d/%m/%Y') if student.birth_date else "—"],
            ["Téléphone", student.phone or "—"],
            ["Email", student.email or "—"],
        ]
        
        table = Table(info_data, colWidths=[5*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5 * cm))
        
        # Frais d'inscription annuels
        story.append(Paragraph("Frais d'Inscription Annuels", h2))
        reg_fees = student.annual_fees.all().order_by('-academic_year__start_date')
        if reg_fees.exists():
            fee_data = [["Année", "Montant", "État"]]
            for fee in reg_fees:
                status = "✓ Payé" if fee.is_paid else "✗ Non payé"
                fee_data.append([
                    str(fee.academic_year),
                    f"{fee.amount:,} DA".replace(',', ' '),
                    status
                ])
            table = Table(fee_data, colWidths=[4*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (1,1), (1,-1), 'RIGHT'),
                ('ALIGN', (2,1), (2,-1), 'CENTER'),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("<i>Aucune information sur les frais d'inscription</i>", normal))
        story.append(Spacer(1, 0.5 * cm))
        
        # Informations parent (supprimé - champs n'existent pas)
        
        # Page 2: Toutes les inscriptions
        story.append(Paragraph(f"INSCRIPTIONS ({enrollments.count()})", h2))
        story.append(Spacer(1, 0.3 * cm))
        
        if enrollments.exists():
            enr_data = [["Groupe", "Année", "Tarif", "Payé", "Reste", "Statut"]]
            for enr in enrollments:
                total_paid = enr.payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
                balance = enr.tariff.amount - total_paid
                status = "✓ Actif" if enr.is_active else "✗ Inactif"
                enr_data.append([
                    enr.cohort.name,
                    str(enr.cohort.academic_year),
                    f"{enr.tariff.amount:,} DA".replace(',', ' '),
                    f"{total_paid:,} DA".replace(',', ' '),
                    f"{balance:,} DA".replace(',', ' '),
                    status
                ])
            
            table = Table(enr_data, repeatRows=1, colWidths=[6.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 1.8*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (2,1), (-2,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("<i>Aucune inscription</i>", normal))
        
        story.append(Spacer(1, 0.5 * cm))
        
        # Page 3: Tous les paiements
        story.append(Paragraph(f"PAIEMENTS ({all_payments.count()})", h2))
        story.append(Spacer(1, 0.3 * cm))
        
        if all_payments.exists():
            payment_data = [["Date", "Groupe", "Montant", "Méthode"]]
            for p in all_payments:
                payment_data.append([
                    p.date.strftime('%d/%m/%Y'),
                    p.enrollment.cohort.name if p.enrollment else "—",
                    f"{p.amount:,} DA".replace(',', ' '),
                    (p.get_method_display() if hasattr(p, 'get_method_display') else '—')
                ])
            
            table = Table(payment_data, repeatRows=1, colWidths=[2*cm, 6.5*cm, 2*cm, 2*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (2,1), (2,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(table)
            
            total_paye = all_payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(f"<b>TOTAL PAYÉ: {total_paye:,} DA</b>".replace(',', ' '), normal))
        else:
            story.append(Paragraph("<i>Aucun paiement</i>", normal))
        
        story.append(Spacer(1, 0.5 * cm))
        
        # Page 4: Toutes les absences
        story.append(Paragraph(f"ABSENCES ({absences.count()})", h2))
        story.append(Spacer(1, 0.3 * cm))
        
        if absences.exists():
            abs_data = [["Date", "Groupe", "Horaire", "Durée"]]
            for att in absences[:50]:  # Limiter à 50 absences max
                abs_data.append([
                    att.session.date.strftime('%d/%m/%Y'),
                    att.session.cohort.name,
                    f"{att.session.start_time.strftime('%H:%M')} - {att.session.end_time.strftime('%H:%M')}",
                    f"{att.session.duration_hours}h"
                ])
            
            table = Table(abs_data, repeatRows=1, colWidths=[2.5*cm, 5.5*cm, 3*cm, 1.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(table)
            
            if absences.count() > 50:
                story.append(Spacer(1, 0.2 * cm))
                story.append(Paragraph(f"<i>... et {absences.count() - 50} absence(s) supplémentaire(s)</i>", normal))
        else:
            story.append(Paragraph("<i>Aucune absence enregistrée ✓</i>", normal))
    
    filename = f"Dossier_{student.last_name}_{student.first_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return _build_pdf_response(filename, f"Dossier Complet - {student.last_name} {student.first_name}", build_story)


@login_required
def download_cohort_complete_zip(request, cohort_id):
    """
    ZIP complet d'un cohort avec TOUS les documents:
    - Fiche synthèse du cohort
    - Liste des étudiants et leurs paiements
    - Paiements du professeur (avec remplaçants)
    - Toutes les listes de présence par séance
    - Rapport des absences
    """
    cohort = get_object_or_404(
        Cohort.objects.select_related('teacher', 'subject', 'level', 'academic_year'),
        id=cohort_id
    )
    
    enrollments = cohort.enrollments.select_related('student', 'tariff').prefetch_related('payments').order_by('student__last_name')
    sessions = cohort.sessions.all().order_by('date')
    teacher_payments = TeacherCohortPayment.objects.filter(cohort=cohort).select_related('teacher').order_by('-payment_date')
    
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        
        # 1. Fiche synthèse du cohort
        def build_synthese(story, styles):
            h1, h2, normal = styles['Heading1'], styles['Heading2'], styles['BodyText']
            h1.fontSize = 14
            h2.fontSize = 14
            normal.fontSize = 14
            
            story.append(Paragraph(f"FICHE SYNTHÈSE - {cohort.name}", h1))
            story.append(Spacer(1, 0.4 * cm))
            
            meta_data = [
                ["Année académique", str(cohort.academic_year)],
                ["Matière", cohort.subject.name],
                ["Niveau", cohort.level.name],
                ["Modalité", cohort.get_modality_display()],
                ["Individuel", "Oui" if cohort.is_individual else "Non"],
                ["Professeur titulaire", cohort.teacher.get_full_name()],
                ["Période", f"{cohort.start_date.strftime('%d/%m/%Y')} → {cohort.end_date.strftime('%d/%m/%Y')}"],
                ["Tarif horaire prof", f"{cohort.teacher_hourly_rate:,} DA/h".replace(',', ' ')],
                ["Nombre d'étudiants", str(enrollments.count())],
                ["Nombre de séances", str(sessions.count())],
                ["Statut", "Terminé" if cohort.is_finished else "En cours"],
            ]
            
            table = Table(meta_data, colWidths=[5*cm, 10*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 14),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ROWHEIGHTS', (0,0), (-1,-1), 0.8*cm),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(table)
            
            # Professeurs remplaçants
            if cohort.substitute_teachers.exists():
                story.append(Spacer(1, 0.4 * cm))
                story.append(Paragraph("Professeurs remplaçants", h2))
                subs = [["Nom"]]
                for sub in cohort.substitute_teachers.all():
                    subs.append([sub.get_full_name()])
                table = Table(subs, colWidths=[15*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 14),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('ROWHEIGHTS', (0,0), (-1,-1), 0.8*cm),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                story.append(table)
        
        synthese_pdf = _generate_pdf_bytes(f"Synthèse {cohort.name}", build_synthese, pagesize=A4)
        zf.writestr("01_Synthese_Cohort.pdf", synthese_pdf)
        
        # 2. Liste des étudiants et paiements
        def build_students(story, styles):
            h1, normal = styles['Heading1'], styles['BodyText']
            h1.fontSize = 16
            normal.fontSize = 10
            
            story.append(Paragraph(f"ÉTUDIANTS - {cohort.name}", h1))
            story.append(Spacer(1, 0.4 * cm))
            
            if enrollments.exists():
                data = [["Code", "Nom", "Tél", "Email", "Tarif", "Payé", "Reste", "Frais Insc."]]
                for enr in enrollments:
                    total_paid = enr.payments.aggregate(total=Coalesce(Sum('amount'), 0))['total']
                    balance = enr.tariff.amount - total_paid
                    registration_status = "✓" if enr.student.has_paid_registration_fee(cohort.academic_year) else "✗"
                    data.append([
                        enr.student.student_code or "—",
                        f"{enr.student.last_name} {enr.student.first_name}",
                        enr.student.phone or "—",
                        enr.student.email or "—",
                        f"{enr.tariff.amount:,}".replace(',', ' '),
                        f"{total_paid:,}".replace(',', ' '),
                        f"{balance:,}".replace(',', ' '),
                        registration_status
                    ])
                
                table = Table(data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 9),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('ALIGN', (4,1), (-1,-1), 'RIGHT'),
                ]))
                story.append(table)
            else:
                story.append(Paragraph("<i>Aucun étudiant inscrit</i>", normal))
        
        students_pdf = _generate_pdf_bytes(f"Étudiants {cohort.name}", build_students)
        zf.writestr("02_Etudiants_Paiements.pdf", students_pdf)
        
        # 3. Paiements du professeur
        def build_teacher_payments(story, styles):
            h1, normal = styles['Heading1'], styles['BodyText']
            h1.fontSize = 18
            normal.fontSize = 10
            
            story.append(Paragraph(f"PAIEMENTS PROFESSEUR - {cohort.name}", h1))
            story.append(Spacer(1, 0.4 * cm))
            
            # Calculer montants/heure sur la base des SEANCES VALIDÉES uniquement
            completed_sessions = [s for s in sessions if s.status == 'COMPLETED']
            validated_hours = sum((Decimal(s.actual_minutes) / Decimal(60)) for s in completed_sessions)
            # Montant dû = Σ(heures validées × tarif horaire applicable) sur les séances validées
            due_amount = sum((Decimal(s.actual_minutes) / Decimal(60)) * Decimal(s.pay_hourly_rate) for s in completed_sessions)
            paid_amount = teacher_payments.aggregate(total=Coalesce(Sum('amount_paid'), Value(0), output_field=DecimalField(max_digits=10, decimal_places=2)))['total']
            balance = due_amount - paid_amount
            
            # Total du groupe (coût prof) complet (toutes séances planifiées)
            group_total_due = sum((Decimal(s.actual_minutes) / Decimal(60)) * Decimal(s.pay_hourly_rate) for s in sessions)

            summary = [
                ["Total du groupe (coût prof)", f"{group_total_due:,.0f} DA".replace(',', ' ')],
                ["Heures validées", f"{float(validated_hours):.2f}h"],
                ["Heures planifiées (total)", f"{sum(s.duration_hours for s in sessions):.2f}h"],
                ["Montant dû", f"{due_amount:,.0f} DA".replace(',', ' ')],
                ["Montant payé", f"{paid_amount:,.0f} DA".replace(',', ' ')],
                ["Reste à payer", f"{balance:,.0f} DA".replace(',', ' ')],
            ]
            
            table = Table(summary, colWidths=[5*cm, 10*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.4 * cm))
            
            if teacher_payments.exists():
                story.append(Paragraph("Détail des paiements", styles['Heading2']))
                pay_data = [["Date", "Professeur", "Montant", "Méthode", "Notes"]]
                for tp in teacher_payments:
                    pay_data.append([
                        tp.payment_date.strftime('%d/%m/%Y'),
                        tp.teacher.get_full_name(),
                        f"{tp.amount_paid:,} DA".replace(',', ' '),
                        tp.get_payment_method_display(),
                        (tp.notes or "")[:30]
                    ])
                
                table = Table(pay_data, repeatRows=1, colWidths=[2.5*cm, 4*cm, 2.5*cm, 2.5*cm, 4.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('ALIGN', (2,1), (2,-1), 'RIGHT'),
                ]))
                story.append(table)
        
        teacher_pay_pdf = _generate_pdf_bytes(f"Paiements Prof {cohort.name}", build_teacher_payments)
        zf.writestr("03_Paiements_Professeur.pdf", teacher_pay_pdf)
        
        # 4. Listes de présence pour chaque séance
        for idx, session in enumerate(sessions, 1):
            att_dict = {a.student_id: a.status for a in Attendance.objects.filter(session=session)}
            STATUS_LABELS = {'PRESENT': 'Présent', 'ABSENT': 'Absent', 'LATE': 'En Retard', 'EXCUSED': 'Excusé'}
            
            def build_attendance(story, styles):
                h1, normal = styles['Heading1'], styles['BodyText']
                story.append(Paragraph(f"PRÉSENCE - Séance {idx}/{sessions.count()}", h1))
                story.append(Spacer(1, 0.2 * cm))
                story.append(Paragraph(f"Date : {session.date.strftime('%d/%m/%Y')} | {session.display_start_time.strftime('%H:%M')} - {session.display_end_time.strftime('%H:%M')}", normal))
                story.append(Paragraph(f"Professeur : {session.teacher.get_full_name()}", normal))
                story.append(Spacer(1, 0.3 * cm))
                
                data = [["N°", "Étudiant", "Statut", "Signature"]]
                for i, enr in enumerate(enrollments, 1):
                    status = STATUS_LABELS.get(att_dict.get(enr.student_id, 'PRESENT'), 'Présent')
                    data.append([i, f"{enr.student.last_name} {enr.student.first_name}", status, ""])
                
                table = Table(data, repeatRows=1, colWidths=[1.2*cm, 7*cm, 4*cm, 5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 9),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ]))
                story.append(table)
            
            att_pdf = _generate_pdf_bytes(f"Présence Séance {idx}", build_attendance)
            filename = f"04_Presences/Seance_{idx:02d}_{session.date.strftime('%Y%m%d')}.pdf"
            zf.writestr(filename, att_pdf)
        
        # 5. Rapport des absences
        def build_absences(story, styles):
            h1, normal = styles['Heading1'], styles['BodyText']
            
            story.append(Paragraph(f"RAPPORT DES ABSENCES - {cohort.name}", h1))
            story.append(Spacer(1, 0.4 * cm))
            
            all_absences = Attendance.objects.filter(
                session__cohort=cohort,
                status='ABSENT'
            ).select_related('student', 'session').order_by('session__date', 'student__last_name')
            
            if all_absences.exists():
                data = [["Date", "Étudiant", "Horaire"]]
                for abs in all_absences:
                    data.append([
                        abs.session.date.strftime('%d/%m/%Y'),
                        f"{abs.student.last_name} {abs.student.first_name}",
                        f"{abs.session.start_time.strftime('%H:%M')} - {abs.session.end_time.strftime('%H:%M')}"
                    ])
                
                table = Table(data, repeatRows=1, colWidths=[3*cm, 7*cm, 5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ]))
                story.append(table)
                
                story.append(Spacer(1, 0.4 * cm))
                story.append(Paragraph(f"<b>TOTAL ABSENCES: {all_absences.count()}</b>", normal))
            else:
                story.append(Paragraph("<i>Aucune absence enregistrée ✓</i>", normal))
        
        abs_pdf = _generate_pdf_bytes(f"Absences {cohort.name}", build_absences)
        zf.writestr("05_Rapport_Absences.pdf", abs_pdf)
    
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    from urllib.parse import quote
    filename = f"Dossier_Complet_{cohort.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.zip"
    encoded_filename = quote(filename)
    response['Content-Disposition'] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
    return response
