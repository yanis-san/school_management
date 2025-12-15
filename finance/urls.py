from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('payment/add/<int:enrollment_id>/', views.add_payment, name='add_payment'),
]