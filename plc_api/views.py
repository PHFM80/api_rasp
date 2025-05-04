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
        plc.connect('192.168.0.3', 0, 0)
        # lee 10 bytes desde la imagen de entradas (PE)
        data = plc.read_area(types.Areas.PE, 0, 0, 10)
        plc.disconnect()
        
        print("DEBUG PE bytes 0–9:", list(data))
        return JsonResponse({'status': 'input bytes printed to console'})
    except Exception as e:
        print("DEBUG error PE:", e)
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