# students/admin.py
from django.contrib import admin
from .models import Student, Enrollment
from finance.models import Installment, Payment

class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0
    readonly_fields = ('due_date', 'amount') # On évite de tricher sur les montants ici
    can_delete = False
    classes = ['collapse'] # Replié par défaut pour gagner de la place

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    classes = ['collapse']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'phone_2', 'email', 'student_code')
    search_fields = ('last_name', 'first_name', 'phone', 'student_code')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'cohort', 'payment_plan', 'tariff', 'balance_due_display', 'is_active')
    list_filter = ('payment_plan', 'is_active', 'cohort')
    search_fields = ('student__last_name', 'student__first_name')
    inlines = [InstallmentInline, PaymentInline] # Tout voir sur une seule page !
    
    def balance_due_display(self, obj):
        # Affiche le reste à payer en rouge si > 0
        balance = obj.balance_due
        if balance > 0:
            return f"{balance} DA (Dû)"
        return "Soldé"
    balance_due_display.short_description = "Reste à payer"