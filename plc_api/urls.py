# api_rasp\plc_api\urls.py

from django.urls import path
from .views import leer_sensor_pi4_view, accionar_actuador_pi4_view

urlpatterns = [
    path('leer-sensor-pi4/', leer_sensor_pi4_view, name='leer-sensor-pi4'),
    path('accionar-actuador-pi4/', accionar_actuador_pi4_view, name='accionar-actuador-pi4'),
]

