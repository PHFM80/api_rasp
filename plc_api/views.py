# plc_api/views.py

from datetime import datetime
from django.http import JsonResponse
from .controller import leer_sensor_en_tiempo_real, accionar_actuador


def leer_sensor_pi4_view(request):
    # Obtener el sensor_id de la solicitud (query string o parámetros)
    sensor_id = request.GET.get("sensor_id", None)

    if not sensor_id:
        return JsonResponse({"error": "Falta el parámetro sensor_id"}, status=400)

    # Llamar a la función para leer el sensor
    result = leer_sensor_en_tiempo_real(sensor_id)

    return JsonResponse(result)

def accionar_actuador_pi4_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        import json
        body = json.loads(request.body)
        id_actuador = int(body.get('id_actuador'))

        resultado = accionar_actuador(id_actuador)  # Esta función cambia el estado y devuelve 'ON' u 'OFF'

        ahora = datetime.now()
        return JsonResponse({
            'id_actuador': id_actuador,
            'accion': resultado,  # 'ON' o 'OFF'
            'fecha': ahora.date().isoformat(),
            'hora': ahora.time().isoformat(timespec='seconds')
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)







    try:
        plc = client.Client()
        plc.connect('192.168.0.3', 0, 0)
        data = plc.read_area(types.Areas.PA, 0, 0, 1)  # VB0.0 en PA
        plc.disconnect()
        return JsonResponse({'actuador': 'ON' if get_bool(data, 0, 0) else 'OFF'})
    except Exception as e:
        return JsonResponse({'error': str(e)})