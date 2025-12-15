# school_management/urls.py
from django.contrib import admin
from django.urls import path,include
from core.views import dashboard
from students.views import create_enrollment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('enrollment/new/', create_enrollment, name='create_enrollment'),
    path('students/', include('students.urls')),
    path('finance/', include('finance.urls'))
]