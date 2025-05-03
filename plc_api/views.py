# plc_api/views.py
# plc_api/views.py
from django.http import JsonResponse
import snap7
from snap7.util import get_int
from snap7 import type as types
from pymodbus.client import ModbusTcpClient
from snap7.util import get_int


def leer_dato_s7_view(request):
    try:
        plc_ip = '192.168.0.3'
        rack = 0
        slot = 0  # para LOGO! 8 suele ser 0

        client = snap7.client.Client()
        client.connect(plc_ip, rack, slot)

        # Leer 2 bytes de memoria (por ejemplo, a partir de MB0)
        data = client.read_area(snap7.types.Areas.MK, 0, 0, 2)
        valor = snap7.util.get_int(data, 0)

        client.disconnect()

        return JsonResponse({'valor_s7': valor})

    except Exception as e:
        return JsonResponse({'error': str(e)})



def leer_dato_modbus_view(request):
    try:
        plc_ip = '192.168.0.3'
        port = 502  # o 510 si usás ese

        client = ModbusTcpClient(plc_ip, port=port)
        client.connect()

        # Leer holding register 0 (ajustá según config del LOGO!)
        rr = client.read_holding_registers(address=0, count=2, unit=1)
        client.close()

        if rr.isError():
            return JsonResponse({'error': 'Error en lectura Modbus'})

        valor = rr.registers[0]
        return JsonResponse({'valor_modbus': valor})

    except Exception as e:
        return JsonResponse({'error': str(e)})



def leer_analogico_ai1(request):
    try:
        plc_ip = '192.168.0.3'      # IP del LOGO!
        rack, slot = 0, 0          # LOGO! 8 suele usar slot=0

        client = snap7.client.Client()
        client.connect(plc_ip, rack, slot)

        # 0x84 = Areas.DB (Data Block); DB number=1; offset=0; length=2 bytes (Word VW0)
        data = client.read_area(0x84, 1, 0, 2)
        valor_raw = get_int(data, 0)

        client.disconnect()
        return JsonResponse({'ai1_raw': valor_raw})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
