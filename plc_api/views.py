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
        plc = client.Client()
        plc.connect('192.168.0.3', 0, 1)   # rack=0, slot=1 para LOGO! 8

        # Leer 2 bytes desde VW0 (área MK)
        data = plc.read_area(types.Areas.MK, 0, 0, 2)
        valor = get_int(data, 0)
        print("DEBUG VW0 data:", list(data), "→", valor)

        plc.disconnect()
        return JsonResponse({'valor_ai1': valor})
    except Exception as e:
        print("ERROR leer_analogico_ai1:", e)
        return JsonResponse({'error': str(e)})



def leer_estado_lampara(request):
    try:
        plc = client.Client()
        plc.connect('192.168.0.3', 0, 0)
        data = plc.read_area(types.Areas.PA, 0, 0, 1)  # VB0.0 en PA
        plc.disconnect()
        return JsonResponse({'lampara': 'ON' if get_bool(data, 0, 0) else 'OFF'})
    except Exception as e:
        return JsonResponse({'error': str(e)})