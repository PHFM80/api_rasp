# plc_api/views.py

from django.http import JsonResponse
import snap7
from snap7.util import get_int
from snap7 import type as types
from snap7 import client
from snap7.util import get_bool
from snap7.util import get_int

def leer_analogico_ai1(request):
    try:
        plc_ip = '192.168.0.3'
        rack = 0
        slot = 1

        plc = client.Client()
        plc.connect(plc_ip, rack, slot)

        data = plc.read_area(types.Areas.MK, 0, 0, 2)  # MK = memoria, 2 bytes desde dirección 0
        valor = get_int(data, 0)

        plc.disconnect()

        return JsonResponse({'valor_ai1': valor})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    


def leer_estado_lampara(request):
    try:
        plc_ip = '192.168.0.3'
        rack = 0
        slot = 0  # LOGO! 8 usualmente usa slot 0

        plc = client.Client()
        plc.connect(plc_ip, rack, slot)

        # Leer 1 byte desde dirección 0 de la memoria (VM0)
        data = plc.read_area(types.Areas.MK, 0, 0, 1)

        # Extraer el bit 0 (VB0.0)
        estado = get_bool(data, 0, 0)

        plc.disconnect()

        return JsonResponse({'lampara': 'ON' if estado else 'OFF'})

    except Exception as e:
        return JsonResponse({'error': str(e)})