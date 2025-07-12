from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

CONFIG_PATH = "config/config.txt"
LOG_PATH = "data/log.csv"
STATE_PATH = "data/system_state.txt"

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        f.write("threshold=40")

if not os.path.exists(STATE_PATH):
    with open(STATE_PATH, "w") as f:
        f.write("OFF")

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
        "humedad": humedad
    })

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