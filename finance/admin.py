# finance/admin.py
from django.contrib import admin
from .models import Tariff, Payment, Installment

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