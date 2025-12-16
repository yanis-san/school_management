# finance/admin.py
from django.contrib import admin
from .models import Tariff, Payment, Installment, Discount, TeacherPayment

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount')
    search_fields = ('name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'amount', 'method', 'date', 'recorded_by')
    list_filter = ('method', 'date')
    search_fields = ('enrollment__student__last_name', 'transaction_id')

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'due_date', 'amount', 'is_paid')
    list_filter = ('is_paid', 'due_date')
    list_editable = ('is_paid',) # Pour marquer payé rapidement depuis la liste

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'type', 'is_active')
    list_filter = ('type', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)

@admin.register(TeacherPayment)
class TeacherPaymentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'payment_date', 'period_start', 'period_end', 'total_amount', 'payment_method', 'recorded_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'proof_reference')
    date_hierarchy = 'payment_date'
    raw_id_fields = ('teacher', 'recorded_by')