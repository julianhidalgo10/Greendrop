# src/relay.py

import RPi.GPIO as GPIO
from config import RELAY_PIN
from sensors import leer_temperatura_humedad
from logger import log_riego

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

def activar_relay():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    temp, hum = leer_temperatura_humedad()
    log_riego("ON", temp, hum)

def desactivar_relay():
    GPIO.output(RELAY_PIN, GPIO.LOW)
    temp, hum = leer_temperatura_humedad()
    log_riego("OFF", temp, hum)

def estado_relay():
    return GPIO.input(RELAY_PIN) == GPIO.HIGH

def liberar_gpio():
    """Libera todos los recursos de GPIO (llamar antes de apagar/reiniciar el server)"""
    GPIO.cleanup()
