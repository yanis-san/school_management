from django.urls import path
from . import views

app_name = 'prospects'

urlpatterns = [
    path('', views.prospect_list, name='list'),
    path('dashboard/', views.prospect_dashboard, name='dashboard'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('add/', views.add_prospect, name='add_prospect'),
    path('<int:prospect_id>/edit/', views.edit_prospect, name='edit_prospect'),
    path('<int:prospect_id>/delete/', views.delete_prospect, name='delete_prospect'),
    path('<int:prospect_id>/convert/', views.convert_to_student, name='convert'),
    path('<int:prospect_id>/cancel-conversion/', views.cancel_conversion, name='cancel_conversion'),
    path('api/prospect/<int:prospect_id>/', views.get_prospect_data, name='get_prospect_data'),
]
