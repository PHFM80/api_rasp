print("Cargando rutas de plc_api")
from django.urls import path
from .views import leer_dato_s7_view, leer_dato_modbus_view

urlpatterns = [
    path('leer_s7/', leer_dato_s7_view, name='leer-s7'),
    path('leer_modbus/', leer_dato_modbus_view, name='leer-modbus'),
]

