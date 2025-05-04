print("Cargando rutas de plc_api")
from django.urls import path
from .views import leer_analogico_ai1, leer_estado_lampara
urlpatterns = [
    path('leer_ai1/', leer_analogico_ai1, name='leer_ai1'),
    path('api/lamp/', leer_estado_lampara, name='leer_estado_lampara'),
]

