#!/usr/bin/env python3
import time
from datetime import datetime
from snap7.client import Client
from snap7 import type as types
from snap7 import util
# IDs fijos
PLC_ID    = 1
SENSOR_ID = 1
LAMP_ID   = 1  # ID del actuador

def leer_sensor():
    plc = Client()
    plc.connect('192.168.0.3', 0, 0)
    data = plc.read_area(types.Areas.DB, 1, 0, 2)
    plc.disconnect()
    return int.from_bytes(data, byteorder='big', signed=False)

def leer_lampara():
    plc = Client()
    plc.connect('192.168.0.3', 0, 0)
    data = plc.read_area(types.Areas.PA, 0, 0, 1)
    plc.disconnect()
    # devuelve "ON" o "OFF"
    return 'ON' if util.get_bool(data, 0, 0) else 'OFF'

def main():
    buffer_sensor = []
    buffer_lamp   = []
    contador      = 0  # cuenta ciclos de 30 s
    while True:
        ts = datetime.now()
        # — cada 30 s: leer sensor
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

        # — cada 60 s (2 ciclos de 30 s): leer actuador
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

        # cada 10 minutos = 20 ciclos de 30 s
        if contador >= 20:
            print("=== Batch 10 min: Sensor ===")
            for e in buffer_sensor:
                print(e)
            print("=== Batch 10 min: Lámpara ===")
            for e in buffer_lamp:
                print(e)
            # reiniciar
            buffer_sensor.clear()
            buffer_lamp.clear()
            contador = 0

        time.sleep(30)

if __name__ == '__main__':
    main()