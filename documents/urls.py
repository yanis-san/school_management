# documents/urls.py
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.select_cohort, name='select_cohort'),
    path('generate/<int:cohort_id>/', views.generate_documents, name='generate_documents'),
]
