# model.py
"""
Funciones relacionadas con el modelo de riesgo de MADly Safe.

- Carga del modelo entrenado (pipeline de scikit-learn en .joblib)
- Función calcular_riesgo(...) que recibe el escenario y devuelve:
    * probabilidad estimada de lesión grave (0–1)
    * lista de 3 franjas alternativas con riesgo algo menor

De momento las franjas alternativas se calculan de forma sencilla
a partir de la probabilidad principal. Más adelante podrías mejorarlo
probando todas las franjas y eligiendo las de menor riesgo.
"""

from pathlib import Path
from typing import Tuple

import joblib
import pandas as pd
import numpy as np


# Ruta por defecto al modelo entrenado (pipeline)
# Esperamos que exista: madly_safe/models/modelo_logistico_2025.joblib
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "modelo_logistico_2025.joblib"

# Caché en memoria del modelo para no recargarlo en cada predicción
_MODELO_CACHE = None


def cargar_modelo(path: Path = MODEL_PATH):
    """
    Carga el modelo entrenado desde disco (solo la primera vez).

    Parameters
    ----------
    path : pathlib.Path
        Ruta al fichero .joblib con el pipeline entrenado.

    Returns
    -------
    modelo : sklearn.Pipeline
        Pipeline con preprocesado + regresión logística.
    """
    global _MODELO_CACHE

    if _MODELO_CACHE is None:
        if not path.exists():
            raise FileNotFoundError(
                "No se ha encontrado el fichero de modelo en: "
                f"{path}. Asegúrate de haber ejecutado el notebook "
                "02_modelo_baseline.ipynb y guardado el modelo."
            )
        _MODELO_CACHE = joblib.load(path)

    return _MODELO_CACHE


# --- Funciones auxiliares para normalizar valores desde la app ---


def _normalizar_dia_semana(dia: str) -> str:
    """
    Arregla pequeños detalles entre los valores de la app y los del dataset.
    """
    if dia == "Miercoles":
        # En el dataset lo tenemos con tilde
        return "Miércoles"
    return dia


def _normalizar_meteo(meteo: str) -> str:
    """
    Normaliza los valores de meteorología de la app
    para aproximarlos a los vistos en el dataset.
    """
    if meteo is None:
        return meteo

    if meteo == "Lluvia debil":
        return "Lluvia débil"
    if meteo == "Lluvia intensa":
        # En los datos aparecía como 'LLuvia intensa' (doble L)
        return "LLuvia intensa"
    if meteo == "Desconocido":
        return "Se desconoce"
    return meteo


# --- Versión DUMMY que usábamos antes (la dejamos por si quieres probar algo) ---


def calcular_riesgo_dummy(tipo_persona, tipo_vehiculo, rango_edad, sexo,
                          distrito, dia, franja, meteo) -> Tuple[float, list]:
    """
    Calcula un riesgo simulado y tres franjas alternativas a partir del hash
    del escenario. Sirve como referencia o para pruebas sin modelo real.
    """
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
    Calcula el riesgo de lesión grave usando el modelo entrenado.

    Parameters
    ----------
    tipo_persona, tipo_vehiculo, rango_edad, sexo, distrito, dia, franja, meteo : str
        Describen el escenario elegido en la app.

    Returns
    -------
    riesgo_principal : float or None
        Probabilidad estimada (entre 0 y 1). None si falta algún dato.
    alternativas : list of (str, float) or None
        Tres franjas alternativas con riesgo algo menor. De momento se
        calculan restando un poco a la probabilidad principal.
    """
    # Si falta algún campo, no podemos predecir
    if None in [tipo_persona, tipo_vehiculo, rango_edad, sexo,
                distrito, dia, franja, meteo]:
        return None, None

    # Normalizamos valores que difieren ligeramente entre app y dataset
    dia_norm = _normalizar_dia_semana(dia)
    meteo_norm = _normalizar_meteo(meteo)

    # Construimos un DataFrame con una sola fila usando los nombres
    # de columnas que el modelo vio durante el entrenamiento.
    datos_escenario = pd.DataFrame(
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

    # Cargamos el modelo y calculamos la probabilidad de clase positiva (grave=1)
    modelo = cargar_modelo()
    proba = modelo.predict_proba(datos_escenario)[0, 1]
    riesgo_principal = float(proba)

    # Generamos tres franjas alternativas con algo menos de riesgo (simplificado).
    alternativas = [
        ("Opción A", max(riesgo_principal - 0.10, 0.001)),
        ("Opción B", max(riesgo_principal - 0.15, 0.001)),
        ("Opción C", max(riesgo_principal - 0.20, 0.001)),
    ]

    return riesgo_principal, alternativas

