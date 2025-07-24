# src/horarios.py

import json
import os
from datetime import datetime, timedelta

HORARIOS_FILE = "horarios.json"
REPOSO_FILE = "ultimo_riego.txt"  # Ya no se usa, pero puedes dejarlo si lo requiere el logger

def cargar_horarios():
    if not os.path.exists(HORARIOS_FILE):
        return []
    with open(HORARIOS_FILE, "r") as f:
        return json.load(f)

def guardar_horarios(lista_horarios):
    with open(HORARIOS_FILE, "w") as f:
        json.dump(lista_horarios, f)

def guardar_ultimo_riego():
    # Mantén la función si la llama el logger, aunque ya no se use para bloquear riegos
    with open(REPOSO_FILE, "w") as f:
        f.write(datetime.now().isoformat())

def tiempo_desde_ultimo_riego():
    # Ya no se usa para bloquear riegos, solo referencia
    if not os.path.exists(REPOSO_FILE):
        return None
    with open(REPOSO_FILE, "r") as f:
        try:
            ultima = datetime.fromisoformat(f.read().strip())
            return (datetime.now() - ultima).total_seconds() / 60  # en minutos
        except:
            return None

def horario_actual_activo():
    """
    Retorna:
      activo (bool): si hay horario activo ahora
      duracion (int): duración del horario activo
      reposo_activo (bool): SIEMPRE False (eliminamos el control de reposo)
    """
    ahora = datetime.now()
    horarios = cargar_horarios()
    for h in horarios:
        inicio = datetime.strptime(h["hora"], "%H:%M").replace(
            year=ahora.year, month=ahora.month, day=ahora.day
        )
        fin = inicio + timedelta(minutes=h.get("duracion", 5))
        if inicio <= ahora < fin:
            return True, h.get("duracion", 5), False
    return False, 0, False
