#!/usr/bin/env python3
import time
import json
from datetime import datetime
import requests
from snap7.client import Client
from snap7 import type as areas
from snap7 import util
import os
import logging

logger = logging.getLogger("pi4_controller")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("controller.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# --- Cargar configuración externa ---
with open("collector_config.json", "r") as f:
    cfg = json.load(f)

# Parámetros PLC
PLC_IP   = cfg["plc_ip"]
PLC_RACK = cfg.get("plc_rack", 0)
PLC_SLOT = cfg.get("plc_slot", 0)

# Intervalos
LECTURA_INTERVALO      = cfg["lectura_intervalo_segundos"]
ENVIO_INTERVALO_CICLOS = cfg["envio_intervalo_ciclos"]

# URLs de la API Django
URL_SENSOR   = cfg["url_sensor"]
URL_ACTUADOR = cfg["url_actuador"]

# ID del controlador
CONTROLADOR_ID = cfg["controlador_id"]

# Dispositivos
SENSORES   = cfg["sensores"]
ACTUADORES = cfg["actuadores"]

# Archivo para guardar payloads fallidos
PENDIENTES_FILE = "pendientes.json"

# Asegurar que existe la estructura inicial
if not os.path.exists(PENDIENTES_FILE):
    with open(PENDIENTES_FILE, "w") as f:
        json.dump({"sensor": [], "actuador": []}, f)

def leer_area(area, db_or_byte, start, size_or_bit, is_bit=False):
    plc = Client()
    plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
    data = plc.read_area(area, db_or_byte, start, 1 if is_bit else size_or_bit)
    plc.disconnect()
    if is_bit:
        return util.get_bool(data, 0, size_or_bit)
    return int.from_bytes(data, byteorder='big', signed=False)

def guardar_pendiente(tipo, payload):
    with open(PENDIENTES_FILE, "r+") as f:
        pendientes = json.load(f)
        pendientes[tipo].append(payload)
        f.seek(0); f.truncate()
        json.dump(pendientes, f)

def procesar_pendientes():
    with open(PENDIENTES_FILE, "r+") as f:
        pendientes = json.load(f)
    nuevos = {"sensor": [], "actuador": []}

    # Reintentar sensores
    for payload in pendientes["sensor"]:
        try:
            r = requests.post(URL_SENSOR, json=payload)
            if r.status_code != 201:
                nuevos["sensor"].append(payload)
        except:
            nuevos["sensor"].append(payload)

    # Reintentar actuadores
    for payload in pendientes["actuador"]:
        try:
            r = requests.post(URL_ACTUADOR, json=payload)
            if r.status_code != 201:
                nuevos["actuador"].append(payload)
        except:
            nuevos["actuador"].append(payload)

    # Escribir sólo los que siguen pendientes
    with open(PENDIENTES_FILE, "w") as f:
        json.dump(nuevos, f)

def enviar(url, payload, tipo):
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 201:
            print(f"Enviado ({tipo}): {payload}")
        else:
            print(f"Error {r.status_code}: {r.text} → guardando pendiente")
            guardar_pendiente(tipo, payload)
    except Exception as e:
        print(f"Excepción al enviar {tipo}: {e} → guardando pendiente")
        guardar_pendiente(tipo, payload)

def enviar_alerta(codigo, controlador_id, sensor_id=None, actuador_id=None):
    alerta = {
        "codigo": codigo,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S"),
        "controlador": controlador_id,
        "sensor": sensor_id if sensor_id else "",
        "actuador": actuador_id if actuador_id else ""
    }

    try:
        response = requests.post(cfg["url_alerta"], json=alerta)
        if response.status_code == 201:
            logger.info(f"Alerta enviada correctamente: {alerta}")
        else:
            logger.error(f"Error al enviar alerta {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Excepción al enviar alerta: {e}")

def leer_sensor_en_tiempo_real(sensor_id):
    from datetime import datetime

    sensor = next((s for s in SENSORES if s["id"] == sensor_id), None)
    if not sensor:
        return {"error": f"Sensor con ID {sensor_id} no encontrado"}

    try:
        plc = Client()
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)

        if not plc.get_connected():
            return {"error": "No se pudo conectar al PLC"}

        val = plc.read_area(areas.Areas.DB, sensor["db"], sensor["start"], sensor["size"])
        plc.disconnect()

        val_int = int.from_bytes(val, byteorder='big', signed=False)
        ts = datetime.now()

        return {
            "valor": val_int,
            "fecha": ts.strftime("%Y-%m-%d"),
            "hora": ts.strftime("%H:%M:%S"),
            "sensor": sensor_id
        }

    except Exception as e:
        return {"error": f"Excepción al leer el sensor: {str(e)}"}

def accionar_actuador(actuador_id):
    """
    Invierte el estado de un actuador físico en el LOGO! 8 y devuelve
    un dict con id_actuador, acción realizada ('ON'/'OFF'), fecha y hora.
    """


    # Buscar configuración del actuador
    actuador_conf = next((a for a in ACTUADORES if a["id"] == actuador_id), None)
    if not actuador_conf:
        return {"error": f"Actuador con ID {actuador_id} no encontrado"}

    # Parámetros de lectura y acción
    area = getattr(areas.Areas, actuador_conf["area"])
    byte_lectura = actuador_conf["byte"]
    bit_lectura  = actuador_conf["bit"]
    # Para la acción usamos estos campos
    area_acc = getattr(areas.Areas, actuador_conf.get("accion_area", actuador_conf["area"]))
    byte_acc  = actuador_conf.get("accion_byte", byte_lectura)
    bit_acc   = actuador_conf.get("accion_bit", bit_lectura)

    try:
        plc = Client()
        plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        if not plc.get_connected():
            return {"error": "No se pudo conectar al PLC"}

        # Leer estado actual
        data = plc.read_area(area, 0 if area!=areas.Areas.DB else byte_lectura, 
                            byte_lectura if area!=areas.Areas.DB else actuador_conf["start"], 1)
        estado_actual = util.get_bool(data, 0, bit_lectura)

        # Invertir estado
        nuevo_estado = not estado_actual
        # Preparar buffer para escribir
        write_data = bytearray(1)
        util.set_bool(write_data, 0, bit_acc, nuevo_estado)
        plc.write_area(area_acc, 0 if area_acc!=areas.Areas.DB else byte_acc, byte_acc if area_acc!=areas.Areas.DB else actuador_conf.get("start", 0), write_data)

        plc.disconnect()

        accion = "ON" if nuevo_estado else "OFF"
        ahora = datetime.now()
        return {
            "id_actuador": actuador_id,
            "accion": accion,
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S")
        }

    except Exception as e:
        # En caso de error, desconectar y reportar
        try: plc.disconnect()
        except: pass
        return {"error": f"Excepción al accionar actuador: {e}"}

def main():
    procesar_pendientes()

    buffer_s = []
    buffer_a = []
    contador = 0

    while True:
        ts = datetime.now()
        fecha = ts.strftime("%Y-%m-%d")
        hora = ts.strftime("%H:%M:%S")

        try:
            # Verificar conexión al PLC
            plc = Client()
            plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
            if not plc.get_connected():
                raise Exception("No conectado")
        except Exception:
            enviar_alerta(1, CONTROLADOR_ID)  # Código 1: PLC desconectado
            time.sleep(LECTURA_INTERVALO)
            continue

        # Leer sensores
        for s in SENSORES:
            try:
                val = plc.read_area(areas.Areas.DB, s["db"], s["start"], s["size"])
                val_int = int.from_bytes(val, byteorder='big', signed=False)

                # Validación fuera de rango (si hay min/max definidos)
                if ("min" in s and val_int < s["min"]) or ("max" in s and val_int > s["max"]):
                    enviar_alerta(2, CONTROLADOR_ID, sensor_id=s["id"])  # Código 2: fuera de rango

                buffer_s.append({
                    "valor": val_int,
                    "fecha": fecha,
                    "hora": hora,
                    "sensor": s["id"]
                })
            except Exception as e:
                logger.error(f"Error al leer sensor {s['id']}: {e}")

        # Leer actuadores
        for a in ACTUADORES:
            try:
                estado = plc.read_area(getattr(areas.Areas, a["area"]), a["byte"], 0, 1)
                estado_bit = util.get_bool(estado, 0, a["bit"])
                estado_str = "ON" if estado_bit else "OFF"

                # Validación simulada: ejemplo → el actuador *debería* estar ON pero no lo está
                if a.get("esperado") == "ON" and not estado_bit:
                    enviar_alerta(3, CONTROLADOR_ID, actuador_id=a["id"])  # Código 3: no arrancó
                elif a.get("esperado") == "OFF" and estado_bit:
                    enviar_alerta(4, CONTROLADOR_ID, actuador_id=a["id"])  # Código 4: no se detuvo

                buffer_a.append({
                    "accion": estado_str,
                    "fecha": fecha,
                    "hora": hora,
                    "actuador": a["id"],
                    "origen_evento": "plc",
                    "controlador": CONTROLADOR_ID,
                    "usuario": ""
                })
            except Exception as e:
                logger.error(f"Error al leer actuador {a['id']}: {e}")

        plc.disconnect()
        contador += 1

        procesar_pendientes()

        if contador >= ENVIO_INTERVALO_CICLOS:
            for entry in buffer_s:
                enviar(URL_SENSOR, entry, "sensor")
            for entry in buffer_a:
                enviar(URL_ACTUADOR, entry, "actuador")
            buffer_s.clear()
            buffer_a.clear()
            contador = 0

        time.sleep(LECTURA_INTERVALO)


if __name__ == "__main__":
    main()
