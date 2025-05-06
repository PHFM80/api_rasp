#!/usr/bin/env python3
import time
from datetime import datetime
import requests
from snap7.client import Client
from snap7 import type as types
from snap7 import util

# IDs fijos
PLC_ID    = 1  # ID del PLC   cambiar PLC_ID por id_controlador
SENSOR_ID = 1  # ID del sensor   cambiar SENSOR_ID por id_sensor
LAMP_ID   = 1  # ID del actuador    cambiar LAMP_ID por id_actuador

# URLs de las APIs locales
URL_SENSOR = "http://192.168.1.37:8000/plantas/datos-sensor-create/"
URL_LAMP   = "http://192.168.1.37:8000/plantas/evento-actuador-create/"

# Función para leer el valor del sensor
def leer_sensor():
    plc = Client()
    plc.connect('192.168.0.3', 0, 0)
    data = plc.read_area(types.Areas.DB, 1, 0, 2)
    plc.disconnect()
    return int.from_bytes(data, byteorder='big', signed=False)

# Función para leer el estado de la lámpara (actuador)
def leer_lampara():
    plc = Client()
    plc.connect('192.168.0.3', 0, 0)
    data = plc.read_area(types.Areas.PA, 0, 0, 1)
    plc.disconnect()
    return 'ON' if util.get_bool(data, 0, 0) else 'OFF'

# Función para enviar datos del sensor
def enviar_datos_sensor(valor, fecha, hora, sensor_id):
    data = {
        "valor": valor,
        "fecha": fecha,
        "hora": hora,
        "sensor": sensor_id,
    }
    try:
        response = requests.post(URL_SENSOR, json=data)
        if response.status_code == 201:
            print(f"Datos del sensor enviados correctamente: {data}")
        else:
            print(f"Error al enviar los datos del sensor: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud de sensor: {e}")

# Función para enviar datos del actuador (lámpara)
def enviar_datos_lampara(estado, fecha, hora, actuador_id):
    data = {
        "accion": estado,
        "fecha": fecha,
        "hora": hora,
        "actuador": actuador_id,
    }
    try:
        response = requests.post(URL_LAMP, json=data)
        if response.status_code == 201:
            print(f"Estado de la lámpara enviado correctamente: {data}")
        else:
            print(f"Error al enviar el estado de la lámpara: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud de lámpara: {e}")

# Función principal
def main():
    buffer_sensor = []
    buffer_lamp   = []
    contador      = 0  # cuenta ciclos de 30 s
    while True:
        ts = datetime.now()
        # Cada 30 segundos: leer sensor
        valor = leer_sensor()
        entry_s = {
            'plc_id':    PLC_ID,
            'sensor_id': SENSOR_ID,
            'fecha':     ts.strftime('%Y-%m-%d'),
            'hora':      ts.strftime('%H:%M:%S'),
            'valor':     valor
        }
        buffer_sensor.append(entry_s)
        print(f"[{ts.strftime('%H:%M:%S')}] Sensor dato: {valor}")

        # Cada 60 segundos (2 ciclos de 30 segundos): leer actuador (lámpara)
        if contador % 2 == 1:
            estado = leer_lampara()
            entry_l = {
                'plc_id':  PLC_ID,
                'lamp_id': LAMP_ID,
                'fecha':   ts.strftime('%Y-%m-%d'),
                'hora':    ts.strftime('%H:%M:%S'),
                'estado':  estado
            }
            buffer_lamp.append(entry_l)
            print(f"[{ts.strftime('%H:%M:%S')}] Lámpara estado: {estado}")

        contador += 1

        # Cada 5 minutos = 10 ciclos de 30 s
        if contador >= 10:
            print("=== Batch 5 minutos: Sensor ===")
            for e in buffer_sensor:
                print(e)
                # Enviar datos del sensor
                enviar_datos_sensor(e['valor'], e['fecha'], e['hora'], e['sensor_id'])
            
            print("=== Batch 5 minutos: Lámpara ===")
            for e in buffer_lamp:
                print(e)
                # Enviar datos del actuador (lámpara)
                enviar_datos_lampara(e['estado'], e['fecha'], e['hora'], e['lamp_id'])

            # Reiniciar buffers
            buffer_sensor.clear()
            buffer_lamp.clear()
            contador = 0

        # Esperar 30 segundos antes de la siguiente iteración
        time.sleep(30)

if __name__ == '__main__':
    main()
