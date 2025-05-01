from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def leer_dato_plc_view(request):
    dato_simulado = 42  # Aquí simulas el valor que devolvería el PLC
    return JsonResponse({'dato_plc': dato_simulado})
