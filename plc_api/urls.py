print("Cargando rutas de plc_api")
from django.urls import path
from .views import leer_dato_plc_view

urlpatterns = [
    path('leer-dato/', leer_dato_plc_view, name='leer-dato-plc'),
]
