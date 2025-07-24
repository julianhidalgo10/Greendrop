# src/sensors.py

import board
import adafruit_dht
from config import DHT_PIN

dhtDevice = adafruit_dht.DHT11(getattr(board, f"D{DHT_PIN}"))

def leer_temperatura_humedad():
    try:
        temperatura = dhtDevice.temperature
        humedad = dhtDevice.humidity
        return temperatura, humedad
    except Exception as e:
        print("Error leyendo sensor:", e)
        return None, None
