# src/logic.py

from sensors import leer_temperatura_humedad
from relay import activar_relay, desactivar_relay, estado_relay
import time

UMBRAL_ON = 40
UMBRAL_OFF = 55
TEMP_MIN = 10
TIEMPO_MIN = 60
TIEMPO_MAX = 600

relay_activado = False
tiempo_activacion = 0

def ciclo_riego():
    global relay_activado, tiempo_activacion
    temperatura, humedad = leer_temperatura_humedad()
    ahora = time.time()

    if temperatura is not None and humedad is not None:
        if temperatura < TEMP_MIN:
            desactivar_relay()
            relay_activado = False
        else:
            if not relay_activado and humedad < UMBRAL_ON:
                activar_relay()
                tiempo_activacion = ahora
                relay_activado = True
            elif relay_activado:
                tiempo_riego = ahora - tiempo_activacion
                if (humedad > UMBRAL_OFF and tiempo_riego > TIEMPO_MIN) or (tiempo_riego > TIEMPO_MAX):
                    desactivar_relay()
                    relay_activado = False
    else:
        desactivar_relay()
        relay_activado = False

