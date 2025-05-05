#!/usr/bin/env python3
import time
from datetime import datetime
from snap7.client import Client
from snap7 import type as types
from snap7 import util
# IDs fijos
PLC_ID    = 1
SENSOR_ID = 1

def leer_sensor():
    plc = Client()
    plc.connect('192.168.0.3', 0, 0)
    data = plc.read_area(types.Areas.DB, 1, 0, 2)
    plc.disconnect()
    # convertir 2 bytes a entero
    valor = int.from_bytes(data, byteorder='big', signed=False)
    return valor

def main():
    buffer = []
    contador = 0
    while True:
        valor = leer_sensor()
        ts = datetime.now()
        entry = {
            'plc_id': PLC_ID,
            'sensor_id': SENSOR_ID,
            'fecha': ts.strftime('%Y-%m-%d'),
            'hora':   ts.strftime('%H:%M:%S'),
            'valor':  valor
        }
        buffer.append(entry)
        print(f"dato: {valor}")
        contador += 1

        # cada 10 muestras de 30 s → 5 min
        if contador >= 10:
            print("=== Batch de 5 min ===")
            for e in buffer:
                print(e)
            buffer.clear()
            contador = 0

        time.sleep(30)

if __name__ == '__main__':
    main()
