# documents/urls.py
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.select_cohort, name='select_cohort'),
    path('generate/<int:cohort_id>/', views.generate_documents, name='generate_documents'),

    # Téléchargement individuel des listes de présence
    path('attendance/session/<int:session_id>/', views.download_session_attendance, name='download_session_attendance'),
    path('attendance/cohort/<int:cohort_id>/', views.download_cohort_attendance, name='download_cohort_attendance'),
]
