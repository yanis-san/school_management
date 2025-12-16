from django.urls import path
from . import views


app_name = 'academics'

urlpatterns = [
    path('cohorts/', views.cohort_list, name='list'),
    path('cohorts/<int:pk>/', views.cohort_detail, name='detail'),
    path('cohorts/<int:pk>/generate/', views.generate_sessions, name='generate_sessions'),
    
    # --- NOUVELLE ROUTE ---
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
]