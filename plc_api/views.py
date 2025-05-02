# plc_api/views.py
# plc_api/views.py
from django.http import JsonResponse
import snap7
from snap7.util import get_int
from snap7.types import Areas
from pymodbus.client import ModbusTcpClient


def leer_dato_s7_view(request):
    try:
        plc_ip = '192.168.0.3'
        rack = 0
        slot = 1

        client = snap7.client.Client()
        client.connect(plc_ip, rack, slot)

        data = client.read_area(types.Areas.DB, 1, 0, 2)  # Lee 2 bytes desde DB1, dirección 0
        valor = get_int(data, 0)

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
        rr = client.read_holding_registers(0, 1, unit=1)
        client.close()

        if rr.isError():
            return JsonResponse({'error': 'Error en lectura Modbus'})

        valor = rr.registers[0]
        return JsonResponse({'valor_modbus': valor})

    except Exception as e:
        return JsonResponse({'error': str(e)})