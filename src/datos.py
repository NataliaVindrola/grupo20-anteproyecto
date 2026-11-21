"""Carga y preparacion de datos del anteproyecto (Grupo 20).

Version recortada de src/datos.py del proyecto de despliegue: solo lo necesario hasta las
tablas de la Guia 4 (sin modelos de prediccion ni particiones). Las reglas de limpieza
viven en src/limpieza.py (limpiar_registro).

Entrada: data/compraventas_0125_bogota.csv y data/ipc.csv.
"""
from __future__ import annotations

import pandas as pd

try:                                   # python -m src.tablas
    from src import limpieza as _L
except ImportError:                    # ejecutado desde dentro de src/
    import limpieza as _L

ORDEN_ZONAS = ["Norte", "Centro", "Sur"]   # ORIP 50N, 50C y 50S
VALOR_MIN = 5_000_000                       # valores por debajo se consideran invalidos
MES_REF = "2026-09"                         # ultimo mes del IPC; define los "pesos constantes"
SEMILLA = 42


def cargar_compraventas(ruta: str = "data/compraventas_0125_bogota.csv") -> pd.DataFrame:
    """Lee el CSV, unifica los dos formatos de fecha y agrega `zona`, `predio` (matricula) y `valor_valido`.

    - `valor`: tal como viene (numerico); `valor_valido` = valor >= VALOR_MIN.
    - Se excluyen las ORIP distintas de 50N/50C/50S y se colapsan las ventas duplicadas
      (misma matricula y fecha): se conserva la de mayor valor y `n_registros_dia` guarda cuantas filas habia.
    """
    df = pd.read_csv(ruta, dtype={"pk": str, "matricula": str, "orip": str}, low_memory=False)
    df = _L.limpiar_registro(df, _L.Bitacora(silencioso=True))
    df = df.rename(columns={"predio_id": "predio"})
    return df.sort_values(["predio", "fecha", "pk"], kind="mergesort").reset_index(drop=True)


def cargar_ipc(ruta: str = "data/ipc.csv") -> pd.Series:
    """Indice mensual de precios (base dic-2018 = 100) indexado por periodo mensual."""
    return _L.cargar_ipc(ruta)


def a_pesos_constantes(df: pd.DataFrame, ipc: pd.Series, mes_ref: str = MES_REF) -> pd.DataFrame:
    """Agrega `valor_real` = valor * ipc[mes_ref] / ipc[mes de la venta]."""
    ref = pd.Period(mes_ref, "M")
    if ref not in ipc.index:
        raise ValueError(f"El mes de referencia {mes_ref} no esta en el IPC.")
    out = df.copy()
    idx = out["fecha"].dt.to_period("M").map(ipc)
    out["valor_real"] = out["valor"] * ipc[ref] / idx
    return out
