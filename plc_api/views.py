# plc_api/views.py

from django.http import JsonResponse
import snap7
from snap7.util import get_int
from snap7 import type as types
from snap7 import client
from snap7.util import get_bool
from snap7.util import get_int

def leer_analogico_ai1(request):
    plc = client.Client()
    plc.connect('192.168.0.3', 0, 1)   # slot=1 para LOGO! 8

    # 1) Entradas digitales (PE)
    pe = plc.read_area(types.Areas.PE, 0, 0, 2)  # bytes 0–1
    bits = []
    for byte_idx in range(len(pe)):
        for bit in range(8):
            bits.append(f"PE[{byte_idx}].{bit} = {get_bool(pe, byte_idx, bit)}")
    print("DEBUG PE bits:", bits)

    # 2) Memoria de marcadores (MK) → words VW0…VW4
    mk = plc.read_area(types.Areas.MK, 0, 0, 10)  # 10 bytes = 5 words
    words = []
    for w in range(5):
        val = get_int(mk, w*2)
        words.append(f"VW{w} = {val}")
    print("DEBUG VW words:", words)

    plc.disconnect()
    return JsonResponse({'status': 'debug printed to console'})



def leer_estado_lampara(request):
    try:
        plc = client.Client()
        plc.connect('192.168.0.3', 0, 0)
        data = plc.read_area(types.Areas.PA, 0, 0, 1)  # VB0.0 en PA
        plc.disconnect()
        return JsonResponse({'lampara': 'ON' if get_bool(data, 0, 0) else 'OFF'})
    except Exception as e:
        return JsonResponse({'error': str(e)})