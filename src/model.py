# model.py
"""
Funciones relacionadas con el modelo de riesgo de MADly Safe.

- Carga del modelo entrenado (pipeline de scikit-learn en .joblib)
- Función calcular_riesgo(...) que recibe el escenario y devuelve:
    * probabilidad estimada de lesión grave (0–1)
    * lista de 3 franjas alternativas con menor riesgo estimado,
      evaluadas con el propio modelo.

Las franjas alternativas se devuelven con una etiqueta legible,
por ejemplo: "18:00–21:59 (Opción A)".
"""

from pathlib import Path
from typing import Tuple

import joblib
import pandas as pd

# Ruta al modelo entrenado que has elegido como final
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "modelo_mejor_2025.joblib"

# Caché en memoria del modelo para no recargarlo en cada predicción
_MODELO_CACHE = None

# Lista de franjas horarias que usaremos para evaluar alternativas
FRANJAS_VALIDAS = [
    "Noche_madrugada",
    "Manana_punta",
    "Manana_media",
    "Tarde",
    "Tarde_punta",
    "Noche",
]

# Etiquetas legibles para cada franja
FRANJA_LABELS = {
    "Noche_madrugada": "00:00–05:59",
    "Manana_punta": "06:00–09:59",
    "Manana_media": "10:00–13:59",
    "Tarde": "14:00–17:59",
    "Tarde_punta": "18:00–21:59",
    "Noche": "22:00–23:59",
}


def cargar_modelo(path: Path = MODEL_PATH):
    """
    Carga el modelo entrenado desde disco (solo la primera vez).
    """
    global _MODELO_CACHE

    if _MODELO_CACHE is None:
        if not path.exists():
            raise FileNotFoundError(
                "No se ha encontrado el fichero de modelo en: "
                f"{path}. Asegúrate de haber guardado el modelo final "
                "como 'models/modelo_mejor_2025.joblib'."
            )
        _MODELO_CACHE = joblib.load(path)

    return _MODELO_CACHE


# --- Normalización de valores desde la app ---


def _normalizar_dia_semana(dia: str) -> str:
    if dia == "Miercoles":
        return "Miércoles"
    return dia


def _normalizar_meteo(meteo: str) -> str:
    if meteo is None:
        return meteo

    if meteo == "Lluvia debil":
        return "Lluvia débil"
    if meteo == "Lluvia intensa":
        return "LLuvia intensa"  # como aparece en algunos datos
    if meteo == "Desconocido":
        return "Se desconoce"
    return meteo


def _df_para_escenario(tipo_persona: str,
                       tipo_vehiculo: str,
                       rango_edad: str,
                       sexo: str,
                       distrito: str,
                       dia_norm: str,
                       franja: str,
                       meteo_norm: str) -> pd.DataFrame:
    """
    Construye un DataFrame de una fila con el formato que espera el modelo.
    """
    return pd.DataFrame(
        [
            {
                "tipo_persona": tipo_persona,
                "tipo_vehiculo": tipo_vehiculo,
                "rango_edad": rango_edad,
                "sexo": sexo,
                "distrito": distrito,
                "dia_semana": dia_norm,
                "franja_horaria": franja,
                "estado_meteorológico": meteo_norm,
            }
        ]
    )


# --- Dummy antiguo (por si necesitas pruebas rápidas) ---


def calcular_riesgo_dummy(tipo_persona, tipo_vehiculo, rango_edad, sexo,
                          distrito, dia, franja, meteo) -> Tuple[float, list]:
    if None in [tipo_persona, tipo_vehiculo, rango_edad, sexo,
                distrito, dia, franja, meteo]:
        return None, None

    clave = f"{tipo_persona}-{tipo_vehiculo}-{rango_edad}-{sexo}-{distrito}-{dia}-{franja}-{meteo}"
    base = (abs(hash(clave)) % 41) + 10  # 10–50
    riesgo_principal = base / 100.0

    alternativas = [
        ("Opción A", max(riesgo_principal - 0.10, 0.01)),
        ("Opción B", max(riesgo_principal - 0.15, 0.01)),
        ("Opción C", max(riesgo_principal - 0.20, 0.01)),
    ]

    return riesgo_principal, alternativas


# --- Versión REAL: usa el modelo entrenado ---


def calcular_riesgo(tipo_persona, tipo_vehiculo, rango_edad, sexo,
                    distrito, dia, franja, meteo) -> Tuple[float, list]:
    """
    Calcula el riesgo de lesión grave usando el modelo entrenado y
    genera hasta tres franjas alternativas más seguras.
    """
    if None in [tipo_persona, tipo_vehiculo, rango_edad, sexo,
                distrito, dia, franja, meteo]:
        return None, None

    dia_norm = _normalizar_dia_semana(dia)
    meteo_norm = _normalizar_meteo(meteo)

    modelo = cargar_modelo()

    # Riesgo franja actual
    df_actual = _df_para_escenario(
        tipo_persona, tipo_vehiculo, rango_edad, sexo,
        distrito, dia_norm, franja, meteo_norm
    )
    proba_actual = modelo.predict_proba(df_actual)[0, 1]
    riesgo_principal = float(proba_actual)

    # Riesgo para todas las franjas
    riesgos_franjas = []
    for fr_opt in FRANJAS_VALIDAS:
        df_opt = _df_para_escenario(
            tipo_persona, tipo_vehiculo, rango_edad, sexo,
            distrito, dia_norm, fr_opt, meteo_norm
        )
        proba_opt = modelo.predict_proba(df_opt)[0, 1]
        riesgos_franjas.append((fr_opt, float(proba_opt)))

    # Filtramos la franja actual
    candidatos = [item for item in riesgos_franjas if item[0] != franja]
    candidatos_ordenados = sorted(candidatos, key=lambda x: x[1])  # menor riesgo primero

    # Priorizar franjas con menor riesgo que la actual
    menores = [c for c in candidatos_ordenados if c[1] < riesgo_principal]
    fusion = menores + [c for c in candidatos_ordenados if c not in menores]

    def _nombre_opcion(idx: int) -> str:
        return f"Opción {chr(ord('A') + idx)}"

    alternativas = []
    for idx, (fr_code, proba_alt) in enumerate(fusion[:3]):
        fr_label = FRANJA_LABELS.get(fr_code, fr_code)
        display = f"{fr_label} ({_nombre_opcion(idx)})"
        alternativas.append((display, float(proba_alt)))

    return riesgo_principal, alternativas
