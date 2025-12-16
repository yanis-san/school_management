# school_management/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import dashboard, login_view, logout_view, signup_view
from students.views import create_enrollment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('', dashboard, name='dashboard'),
    path('enrollment/new/', create_enrollment, name='create_enrollment'),
    path('students/', include('students.urls')),
    path('finance/', include('finance.urls')),
    path('academics/', include('academics.urls')),
    path('documents/', include('documents.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)