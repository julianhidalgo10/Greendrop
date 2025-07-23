from flask import Flask, jsonify, request, send_from_directory
import threading
import time
import schedule
import os

app = Flask(__name__, static_folder="static")

# Estado global
humedad_actual = 45  # Valor inicial
umbral_humedad = 40  # Valor por defecto
estado_riego = "OFF" # ON/OFF

# Función para leer la configuración desde config.txt
def read_config():
    config = {}
    if os.path.exists("config/config.txt"):
        with open("config/config.txt", "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                config[key] = value
    return config

# Función para actualizar la configuración en config.txt
def update_config(threshold=None, hora=None, duracion=None):
    config = read_config()
    if threshold:
        config["threshold"] = str(threshold)
    if hora:
        config["hora"] = str(hora)
    if duracion:
        config["duracion"] = str(duracion)

    # Guardar en config.txt
    with open("config/config.txt", "w") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

# API: Obtener estado actual y configuración
@app.route("/api/status", methods=["GET"])
def api_status():
    config = read_config()
    threshold = config.get("threshold", 40)
    estado = read_system_state()
    humedad = None
    try:
        with open(LOG_PATH, "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                parts = line.strip().split(',')
                if len(parts) >= 2 and parts[1].isdigit():
                    humedad = int(parts[1])
                    break
    except FileNotFoundError:
        pass
    return jsonify({
        "estado": estado,
        "umbral": threshold,
        "humedad": humedad
    })

# API: Actualizar umbral, hora y duración
@app.route("/api/configuracion", methods=["POST"])
def set_configuracion():
    data = request.get_json()
    umbral = data.get("umbral", 40)
    hora = data.get("hora", "06:00")
    duracion = data.get("duracion", 10)

    # Actualizar la configuración en config.txt
    update_config(threshold=umbral, hora=hora, duracion=duracion)

    return jsonify({"mensaje": "Configuración actualizada", "umbral": umbral, "hora": hora, "duracion": duracion})

# Función del riego automático programado
def riego_programado():
    print("[RIEGO PROGRAMADO] Activando riego automático...")
    cambiar_estado_riego("ON")
    time.sleep(programacion_riego["duracion"])
    cambiar_estado_riego("OFF")
    print("[RIEGO PROGRAMADO] Riego automático finalizado.")

# Endpoints para consultar y modificar programación del riego automático
@app.route('/api/programado', methods=['GET'])
def obtener_programacion():
    config = read_config()
    return jsonify({
        "hora": config.get("hora", "06:00"),
        "duracion": config.get("duracion", 10)
    })

@app.route('/api/programado', methods=['POST'])
def modificar_programacion():
    data = request.get_json()
    hora = data.get('hora')
    duracion = data.get('duracion')

    # Validaciones básicas
    if not isinstance(hora, str) or len(hora) != 5 or hora[2] != ':':
        return jsonify({"error": "Formato de hora inválido, debe ser HH:MM"}), 400
    if not isinstance(duracion, int) or duracion <= 0:
        return jsonify({"error": "Duración inválida, debe ser entero positivo"}), 400

    # Actualizar configuración global
    update_config(threshold=None, hora=hora, duracion=duracion)

    return jsonify({"mensaje": "Programación actualizada", "programacion": {"hora": hora, "duracion": duracion}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)