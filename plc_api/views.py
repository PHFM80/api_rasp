# plc_api/views.py

from django.http import JsonResponse
import snap7
from snap7.util import get_int
from snap7 import type as types
from snap7 import client
from snap7.util import get_bool
from snap7.util import get_int
from snap7.client import Client                  # Cliente Snap7 para S7/LOGO!8 :contentReference[oaicite:0]{index=0}
from snap7.types import Areas   


def leer_analogico_ai1(request):
    """
    Vista Django que lee las palabras VW0 y VW1 de la memoria variable (VM)
    del LOGO!8 expuesto como DataBlock 1, y las devuelve en JSON.
    """

    plc_ip = '192.168.0.3'                         # IP configurada del LOGO! 
    rack, slot = 0, 0                              # TSAP típicos para LOGO!8 :contentReference[oaicite:4]{index=4}

    plc = Client()                                 # Crear instancia de cliente :contentReference[oaicite:5]{index=5}
    try:
        plc.connect(plc_ip, rack, slot)            # Conectar al LOGO! :contentReference[oaicite:6]{index=6}

        # Leer 4 bytes del DataBlock 1 (VW0 y VW1 son 2 palabras = 4 bytes)
        data = plc.read_area(Areas.DB, 1, 0, 4)     # Lee DB1 desde offset 0, longitud 4 :contentReference[oaicite:7]{index=7}

        # Convertir cada par de bytes a entero sin signo (0–65535)
        vw0 = int.from_bytes(data[0:2], byteorder='big', signed=False)  # VW0 (0–1000 → 0–10 V) :contentReference[oaicite:8]{index=8}
        vw1 = int.from_bytes(data[2:4], byteorder='big', signed=False)  # VW1 (si lo configuraste) :contentReference[oaicite:9]{index=9}

        return JsonResponse({'VW0': vw0, 'VW1': vw1})                  # Devolver JSON :contentReference[oaicite:10]{index=10}

    except Exception as e:
        # En caso de error, devolver mensaje y código 500
        return JsonResponse({'error': str(e)}, status=500)            # Buenas prácticas de API :contentReference[oaicite:11]{index=11}

    finally:
        plc.disconnect()                          # Asegurar cierre de conexión 



def leer_estado_lampara(request):
    try:
        plc = client.Client()
        plc.connect('192.168.0.3', 0, 0)
        data = plc.read_area(types.Areas.PA, 0, 0, 1)  # VB0.0 en PA
        plc.disconnect()
        return JsonResponse({'lampara': 'ON' if get_bool(data, 0, 0) else 'OFF'})
    except Exception as e:
        return JsonResponse({'error': str(e)})