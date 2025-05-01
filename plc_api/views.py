# plc_api/views.py

from django.http import JsonResponse
import snap7

def leer_dato_plc_view(request):
    try:
        # Configuración de conexión
        plc_ip = '192.168.0.3'  # IP del LOGO! 8, ajustala si es distinta
        rack = 0
        slot = 1  # usualmente 1 en LOGO! 8

        # Crear cliente y conectar
        client = snap7.client.Client()
        client.connect(plc_ip, rack, slot)

        # Leer área de entrada (inputs) - 0x81 es el código para entradas (PE)
        data = client.read_area(snap7.types.Areas.PE, 0, 0, 1)  # leer 1 byte desde la dirección 0

        # La entrada analógica I7 está mapeada como parte de las entradas analógicas, y puede necesitar otra dirección
        # En LOGO! 8 a veces se accede por DB (data block) o de manera especial, según configuración
        # Este ejemplo asume acceso básico digital. Para analógicas podría requerir bloques DB y lectura de 2 bytes

        client.disconnect()

        valor = int.from_bytes(data, byteorder='big')  # convertir byte a int
        return JsonResponse({'dato_plc': valor})
    
    except Exception as e:
        return JsonResponse({'error': str(e)})
