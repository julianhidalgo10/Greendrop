from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

CONFIG_PATH = "config/config.txt"
LOG_PATH = "data/log.csv"
STATE_PATH = "data/system_state.txt"

# Crear archivo de configuración si no existe
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        f.write("threshold=40\nhora=06:00\nduracion=10\n")

# Crear archivo de estado si no existe
if not os.path.exists(STATE_PATH):
    with open(STATE_PATH, "w") as f:
        f.write("OFF")

# Función para leer el umbral desde el archivo de configuración
def read_threshold():
    with open(CONFIG_PATH, "r") as f:
        for line in f:
            if line.startswith("threshold"):
                return int(line.strip().split("=")[1])
    return 40  # Valor por defecto si no se encuentra

# Función para leer la hora desde el archivo de configuración
def read_hora():
    with open(CONFIG_PATH, "r") as f:
        for line in f:
            if line.startswith("hora"):
                return line.strip().split("=")[1]
    return "06:00"  # Hora por defecto si no se encuentra

# Función para leer la duración desde el archivo de configuración
def read_duracion():
    with open(CONFIG_PATH, "r") as f:
        for line in f:
            if line.startswith("duracion"):
                return int(line.strip().split("=")[1])
    return 10  # Duración por defecto si no se encuentra

# Función para leer el estado del sistema
def read_system_state():
    try:
        with open(STATE_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "OFF"

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route('/api/status', methods=['GET'])
def get_status():
    threshold = read_threshold()
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

@app.route("/api/configuracion", methods=["POST"])
def set_configuracion():
    data = request.get_json()
    umbral = data.get("umbral", 40)
    hora = data.get("hora", "06:00")
    duracion = data.get("duracion", 10)

    # Actualizar el archivo de configuración
    with open(CONFIG_PATH, "w") as f:
        f.write(f"threshold={umbral}\n")
        f.write(f"hora={hora}\n")
        f.write(f"duracion={duracion}\n")

    return jsonify({"mensaje": "Configuración actualizada", "umbral": umbral, "hora": hora, "duracion": duracion})

@app.route("/api/umbral", methods=["POST"])
def set_umbral():
    data = request.get_json()
    nuevo_umbral = int(data.get("umbral", 40))
    with open(CONFIG_PATH, "w") as f:
        f.write(f"threshold={nuevo_umbral}")
    return jsonify({"message": "Umbral actualizado", "nuevo_umbral": nuevo_umbral})

@app.route("/api/riego", methods=["POST"])
def set_riego():
    data = request.get_json()
    nuevo_estado = data.get("estado", "OFF").upper()
    if nuevo_estado not in ["ON", "OFF"]:
        return jsonify({"error": "Estado inválido"}), 400
    with open(STATE_PATH, "w") as f:
        f.write(nuevo_estado)
    return jsonify({"message": f"Riego cambiado a {nuevo_estado}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)