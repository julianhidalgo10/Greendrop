from flask import Flask, jsonify, request, send_from_directory
import threading
import time
import schedule
import os

app = Flask(__name__, static_folder="static")

# Estado global simulado
humedad_actual = 45  # Simulación: valor inicial
umbral_humedad = 40  # Valor por defecto
estado_riego = "OFF" # ON/OFF

# Configuración inicial del riego programado (modificable desde API)
programacion_riego = {
    "hora": "06:00",      # Hora en formato HH:MM
    "duracion": 10        # Duración en segundos
}

# Cambiar estado del riego
def cambiar_estado_riego(nuevo_estado):
    global estado_riego
    estado_riego = nuevo_estado
    # Guardar estado en archivo
    with open("data/system_state.txt", "w") as f:
        f.write(estado_riego)
    print(f"[ESTADO RIEGO] Cambiado a: {estado_riego}")

# Ruta para servir la página principal
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# API: Obtener estado actual
@app.route("/api/status")
def api_status():
    return jsonify({
        "humedad": humedad_actual,
        "umbral": umbral_humedad,
        "estado": estado_riego
    })

# API: Actualizar umbral
@app.route("/api/umbral", methods=["POST"])
def api_umbral():
    global umbral_humedad
    data = request.get_json()
    umbral = data.get("umbral")
    if umbral is None or not (0 <= umbral <= 100):
        return jsonify({"error": "Umbral inválido"}), 400
    umbral_humedad = umbral
    return jsonify({"mensaje": "Umbral actualizado", "umbral": umbral_humedad})

# API: Control manual del riego
@app.route("/api/riego", methods=["POST"])
def api_riego():
    data = request.get_json()
    estado = data.get("estado")
    if estado not in ("ON", "OFF"):
        return jsonify({"error": "Estado inválido"}), 400
    cambiar_estado_riego(estado)
    return jsonify({"mensaje": f"Riego {estado} exitoso"})

# Función del riego automático programado
def riego_programado():
    print("[RIEGO PROGRAMADO] Activando riego automático...")
    cambiar_estado_riego("ON")
    time.sleep(programacion_riego["duracion"])
    cambiar_estado_riego("OFF")
    print("[RIEGO PROGRAMADO] Riego automático finalizado.")

# Scheduler para riego programado con lectura dinámica de hora y duración
def start_scheduler():
    while True:
        schedule.clear()
        schedule.every().day.at(programacion_riego["hora"]).do(riego_programado)
        schedule.run_pending()
        time.sleep(1)

# Endpoints para consultar y modificar programación del riego automático
@app.route('/api/programado', methods=['GET'])
def obtener_programacion():
    return jsonify(programacion_riego)

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
    programacion_riego["hora"] = hora
    programacion_riego["duracion"] = duracion

    return jsonify({"mensaje": "Programación actualizada", "programacion": programacion_riego})

# Se inicia el scheduler en un hilo aparte para no bloquear Flask
scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    # Crear carpeta data si no existe
    if not os.path.exists("data"):
        os.makedirs("data")
    # Crear archivo de estado si no existe
    if not os.path.exists("data/system_state.txt"):
        with open("data/system_state.txt", "w") as f:
            f.write("OFF")

    app.run(host="0.0.0.0", port=5000)