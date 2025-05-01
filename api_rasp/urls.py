from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('plc_api.urls')),  # Esto incluye las URLs de la app
]
