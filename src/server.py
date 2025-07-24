import threading
import time
import os
import signal
from flask import Flask, jsonify, send_from_directory, request
from sensors import leer_temperatura_humedad
from relay import activar_relay, desactivar_relay, estado_relay, liberar_gpio
from logger import leer_registros, log_error
from horarios import cargar_horarios, guardar_horarios, horario_actual_activo, guardar_ultimo_riego
from config import UMBRAL_INICIAL, REPOSO_MINUTOS

app = Flask(__name__, static_folder="static")

UMBRAL = UMBRAL_INICIAL
UMBRAL_FILE = "umbral.txt"
REPOSO_MIN_FILE = "reposo_min.txt"

def cargar_umbral():
    global UMBRAL
    if os.path.exists(UMBRAL_FILE):
        with open(UMBRAL_FILE) as f:
            try:
                UMBRAL = float(f.read().strip())
            except Exception as e:
                log_error(f"Error cargando umbral: {e}")

def guardar_umbral(valor):
    with open(UMBRAL_FILE, "w") as f:
        f.write(str(valor))

def cargar_reposo():
    if os.path.exists(REPOSO_MIN_FILE):
        with open(REPOSO_MIN_FILE) as f:
            try:
                return int(f.read().strip())
            except Exception as e:
                log_error(f"Error cargando reposo: {e}")
    return REPOSO_MINUTOS

def guardar_reposo(valor):
    with open(REPOSO_MIN_FILE, "w") as f:
        f.write(str(valor))

def temperatura_raspberry():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_mil = int(f.read())
            return round(temp_mil / 1000, 1)
    except Exception as e:
        log_error(f"No se pudo leer la temperatura de la Pi: {e}")
        return None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/status')
def status():
    temp, hum = leer_temperatura_humedad()
    relay = estado_relay()
    activo, duracion, reposo_activo = horario_actual_activo()
    return jsonify({
        "temperatura": temp,
        "humedad": hum,
        "umbral": UMBRAL,
        "relay": "ON" if relay else "OFF",
        "reposo_min": cargar_reposo(),
        "reposo_activo": reposo_activo,
        "temp_raspberry": temperatura_raspberry()
    })

@app.route('/api/riego', methods=['POST'])
def set_riego():
    data = request.get_json()
    accion = data.get("accion", "").upper()
    if accion == "ON":
        activar_relay()
        guardar_ultimo_riego()
        return jsonify({"relay": "ON", "ok": True, "mensaje": "Riego activado manualmente."})
    elif accion == "OFF":
        desactivar_relay()
        return jsonify({"relay": "OFF", "ok": True, "mensaje": "Riego desactivado manualmente."})
    else:
        return jsonify({"error": "Acción inválida"}), 400

@app.route('/api/umbral', methods=['POST'])
def set_umbral():
    global UMBRAL
    data = request.get_json()
    nuevo_umbral = data.get("umbral")
    try:
        nuevo_umbral = float(nuevo_umbral)
        UMBRAL = nuevo_umbral
        guardar_umbral(UMBRAL)
        return jsonify({"umbral": UMBRAL, "ok": True, "mensaje": "Umbral actualizado."})
    except Exception as e:
        log_error(f"Error actualizando umbral: {e}")
        return jsonify({"error": "Umbral inválido"}), 400

@app.route("/api/registros", methods=["GET"])
def api_registros():
    registros = leer_registros()
    return jsonify({"registros": registros})

@app.route("/api/registros", methods=["DELETE"])
def borrar_registros():
    try:
        os.remove("registro_riego.csv")
    except Exception as e:
        log_error(f"Error borrando registros: {e}")
    return jsonify({"ok": True, "mensaje": "Historial eliminado."})

@app.route("/api/horarios", methods=["GET"])
def get_horarios():
    return jsonify({"horarios": cargar_horarios()})

@app.route("/api/horarios", methods=["POST"])
def set_horarios():
    data = request.get_json()
    horarios = data.get("horarios")
    if not isinstance(horarios, list):
        return jsonify({"error": "Formato inválido"}), 400
    for h in horarios:
        if not isinstance(h, dict) or "hora" not in h or "duracion" not in h:
            return jsonify({"error": "Formato de horario inválido"}), 400
    guardar_horarios(horarios)
    return jsonify({"ok": True, "mensaje": "Horarios actualizados."})

@app.route("/api/reposo", methods=["POST"])
def set_reposo():
    data = request.get_json()
    valor = data.get("reposo")
    try:
        valor = int(valor)
        guardar_reposo(valor)
        return jsonify({"ok": True, "mensaje": f"Reposo mínimo actualizado a {valor} min."})
    except Exception as e:
        log_error(f"Error actualizando reposo: {e}")
        return jsonify({"error": "Valor inválido"}), 400

def riego_programado():
    while True:
        activo, duracion, reposo_activo = horario_actual_activo()
        temp, hum = leer_temperatura_humedad()
        print(f"Activo: {activo}, Reposo: {reposo_activo}, Humedad: {hum}, Umbral: {UMBRAL}")
        if activo and not reposo_activo and hum is not None and hum < UMBRAL:
            if not estado_relay():
                print("Activando riego")
                activar_relay()
                guardar_ultimo_riego()
        else:
            if estado_relay():
                print("Desactivando riego")
                desactivar_relay()
        time.sleep(30)

def manejo_senal(signum, frame):
    print(f"\n[GreenDrop] Señal recibida ({signum}). Liberando recursos...")
    liberar_gpio()
    print("[GreenDrop] GPIO liberado y servidor apagado.")
    exit(0)

signal.signal(signal.SIGINT, manejo_senal)
signal.signal(signal.SIGTERM, manejo_senal)

if __name__ == "__main__":
    cargar_umbral()
    t = threading.Thread(target=riego_programado, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
