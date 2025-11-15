# etl.py
"""
Módulo de ETL para MADly Safe.

Aquí centralizamos la carga y preparación de los datos de accidentalidad
(de momento, solo 2025). La idea es que cualquier parte del proyecto
(app, notebooks, etc.) use estas funciones en lugar de repetir código.
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


# Nombre del fichero de datos de 2025 (relativo a la carpeta data/)
DATA_FILE_2025 = "2025_Accidentalidad.xlsx"


def _ruta_data() -> Path:
    """
    Devuelve la ruta a la carpeta data/ partiendo de este archivo.

    src/etl.py
    └── .. (src)
        └── .. (madly_safe)
            └── data/
    """
    return Path(__file__).resolve().parents[1] / "data"


def cargar_datos_brutos_2025() -> pd.DataFrame:
    """
    Carga el fichero Excel de 2025 tal cual viene del portal.

    Returns
    -------
    df : pandas.DataFrame
        Datos originales sin transformar.
    """
    ruta_fichero = _ruta_data() / DATA_FILE_2025
    if not ruta_fichero.exists():
        raise FileNotFoundError(f"No se ha encontrado el fichero {ruta_fichero}")

    df = pd.read_excel(ruta_fichero)
    return df


def _añadir_variables_tiempo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade columnas relacionadas con fecha y hora:
    - fecha (datetime)
    - hora_num (0–23)
    - dia_semana_num (0=Lunes,...,6=Domingo)
    - dia_semana (nombre en castellano)
    - es_fin_semana (bool)
    - franja_horaria (categoría acorde a la app)
    """
    df = df.copy()

    # Aseguramos tipo datetime
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Hora como entero (0–23). errors='coerce' por si alguna fila viene mal.
    df["hora_num"] = pd.to_datetime(df["hora"], format="%H:%M:%S", errors="coerce").dt.hour

    # Día de la semana
    df["dia_semana_num"] = df["fecha"].dt.dayofweek
    map_dia = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }
    df["dia_semana"] = df["dia_semana_num"].map(map_dia)

    # Fin de semana
    df["es_fin_semana"] = df["dia_semana"].isin(["Sábado", "Domingo"])

    # Franja horaria alineada con la app
    def asignar_franja(hora):
        if pd.isna(hora):
            return "Desconocida"
        hora = int(hora)
        if 0 <= hora <= 5:
            return "Noche_madrugada"
        elif 6 <= hora <= 9:
            return "Manana_punta"
        elif 10 <= hora <= 13:
            return "Manana_media"
        elif 14 <= hora <= 17:
            return "Tarde"
        elif 18 <= hora <= 21:
            return "Tarde_punta"
        elif 22 <= hora <= 23:
            return "Noche"
        else:
            return "Desconocida"

    df["franja_horaria"] = df["hora_num"].apply(asignar_franja)

    return df


def _añadir_objetivo_grave(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea la variable objetivo 'grave':

    grave = 1 si cod_lesividad en {3,4}
    grave = 0 si cod_lesividad en {1,2,5,6,7,14}
    NaN  en el resto de casos (sin info de lesividad)

    Además, la columna grave se deja como entero (0/1) donde se conoce.
    """
    df = df.copy()

    df["grave"] = np.nan

    cond_grave = df["cod_lesividad"].isin([3, 4])
    cond_no_grave = df["cod_lesividad"].isin([1, 2, 5, 6, 7, 14])

    df.loc[cond_grave, "grave"] = 1
    df.loc[cond_no_grave, "grave"] = 0

    # Convertimos a entero donde no es NaN
    df.loc[df["grave"].notna(), "grave"] = df.loc[df["grave"].notna(), "grave"].astype(int)

    return df


def preparar_datos_2025(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aplica todas las transformaciones necesarias a los datos de 2025.

    Parameters
    ----------
    df : pandas.DataFrame
        Datos brutos tal y como salen del Excel.

    Returns
    -------
    df_completo : pandas.DataFrame
        DataFrame con columnas adicionales (tiempo, franja, objetivo, etc.).
    df_target : pandas.DataFrame
        Subconjunto de df_completo donde la variable 'grave' está definida (0/1).
    """
    df_proc = _añadir_variables_tiempo(df)
    df_proc = _añadir_objetivo_grave(df_proc)

    df_target = df_proc.dropna(subset=["grave"]).copy()

    return df_proc, df_target


def cargar_y_preparar_2025() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Función de alto nivel que:

    1) Carga el Excel de 2025 desde data/
    2) Aplica las transformaciones de tiempo y la creación del objetivo 'grave'

    Returns
    -------
    df_proc : pandas.DataFrame
        Datos de 2025 con columnas derivadas.
    df_target : pandas.DataFrame
        Solo filas con objetivo 'grave' definido (0/1).
    """
    df_raw = cargar_datos_brutos_2025()
    df_proc, df_target = preparar_datos_2025(df_raw)
    return df_proc, df_target
