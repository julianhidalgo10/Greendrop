import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuración de pines y variables
DHT_PIN = board.D4         # GPIO4 (pin físico 7)
RELAY_PIN = 17             # GPIO17 (pin físico 11)
UMBRAL_ON = 40             # humedad para activar riego
UMBRAL_OFF = 55            # humedad para desactivar riego
TEMP_MIN = 10              # °C para no regar si hace frío
TEMP_MAX = 35              # °C para alerta o riego reforzado (opcional)
HORARIOS = [
    (6, 9),     # 6:00am a 9:00am
    (18, 21),   # 6:00pm a 9:00pm
]

# Ruta de configuración
CONFIG_PATH = "config/config.txt"

# Función para verificar si está en el horario permitido
def en_horario_permitido():
    ahora = time.localtime().tm_hour
    for inicio, fin in HORARIOS:
        if inicio <= ahora < fin:
            return True
    return False

# Función de riego y control de relay
def control_riego():
    dhtDevice = adafruit_dht.DHT11(DHT_PIN)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    temperatura = None
    humedad = None
    
    try:
        temperatura = dhtDevice.temperature
        humedad = dhtDevice.humidity
    except Exception as e:
        print("Error leyendo sensor:", e)
    
    if humedad is not None and temperatura is not None:
        print(f"Temp={temperatura:0.1f}C  Humedad={humedad:0.1f}%")

        # Verificar si está en horario permitido
        if not en_horario_permitido():
            print("Fuera del horario de riego, relay apagado.")
            GPIO.output(RELAY_PIN, GPIO.LOW)
            return "Fuera del horario de riego", 200
        
        # Lógica de control de riego
        if humedad < UMBRAL_ON and temperatura > TEMP_MIN:  # No regar si hace frío
            GPIO.output(RELAY_PIN, GPIO.HIGH)  # Activa el relay
            return "Riego activado", 200
        elif humedad > UMBRAL_OFF:
            GPIO.output(RELAY_PIN, GPIO.LOW)  # Desactiva el relay
            return "Riego desactivado", 200
    return "Error con el sensor", 500

@app.route("/api/riego", methods=["POST"])
def set_riego():
    """Endpoint para controlar el estado del riego (activar o desactivar)."""
    data = request.get_json()
    estado = data.get("estado", "OFF").upper()
    if estado not in ["ON", "OFF"]:
        return jsonify({"error": "Estado inválido"}), 400
    
    if estado == "ON":
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        return jsonify({"message": "Riego activado"}), 200
    else:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        return jsonify({"message": "Riego desactivado"}), 200

@app.route("/api/status", methods=["GET"])
def api_status():
    """Endpoint para obtener el estado actual del sistema de riego y la humedad."""
    estado_riego = "ON" if GPIO.input(RELAY_PIN) else "OFF"
    return jsonify({
        "estado_riego": estado_riego,
        "umbral": UMBRAL_ON,
        "humedad": None  # Este valor puede ser calculado o traído de un log de humedad
    })

@app.route('/api/configuracion', methods=["POST"])
def set_configuracion():
    """Actualizar umbral, hora y duración en la configuración."""
    data = request.get_json()
    umbral = data.get("umbral", 40)
    hora = data.get("hora", "06:00")
    duracion = data.get("duracion", 10)

    # Actualizar la configuración en un archivo (config.txt)
    with open(CONFIG_PATH, "w") as f:
        f.write(f"threshold={umbral}\n")
        f.write(f"hora={hora}\n")
        f.write(f"duracion={duracion}\n")

    global UMBRAL_ON
    UMBRAL_ON = umbral  # Actualizamos el umbral globalmente
    
    return jsonify({"mensaje": "Configuración actualizada", "umbral": umbral, "hora": hora, "duracion": duracion})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)