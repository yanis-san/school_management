from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Paiements étudiants
    path('payment/add/<int:enrollment_id>/', views.add_payment, name='add_payment'),

    # Paie des professeurs
    path('payroll/', views.teacher_payroll_list, name='teacher_payroll_list'),
    path('payroll/teacher/<int:teacher_id>/', views.teacher_payroll_detail, name='teacher_payroll_detail'),
    path('payroll/teacher/<int:teacher_id>/pay/', views.record_teacher_payment, name='record_teacher_payment'),
]