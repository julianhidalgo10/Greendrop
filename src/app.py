import schedule
import threading
import time

# Función que se ejecutará a la hora programada
def riego_programado():
    print("[RIEGO PROGRAMADO] Activando riego automático...")
    cambiar_estado_riego("ON")
    time.sleep(10)  # duración del riego en segundos
    cambiar_estado_riego("OFF")
    print("[RIEGO PROGRAMADO] Riego automático finalizado.")

# Función que corre en un hilo paralelo para ejecutar el horario
def start_scheduler():
    schedule.every().day.at("06:00").do(riego_programado)  # hora programada

    while True:
        schedule.run_pending()
        time.sleep(1)

# Se inicia el programador como hilo independiente
scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()