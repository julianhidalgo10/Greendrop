# src/logger.py

import csv
import logging
from datetime import datetime

LOG_FILE = "registro_riego.csv"

# Configura log avanzado a archivo del sistema
logging.basicConfig(
    filename='/var/log/greendrop.log', 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def log_riego(evento, temperatura, humedad):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now, evento, temperatura, humedad])
    logging.info(f"Evento: {evento} | Temp: {temperatura} | Hum: {humedad}")

def log_error(mensaje):
    logging.error(mensaje)

def leer_registros():
    try:
        with open(LOG_FILE, "r") as f:
            return list(csv.reader(f))
    except FileNotFoundError:
        return []
