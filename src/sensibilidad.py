"""Sensibilidad de la valorizacion (retroalimentacion de la Guia 4).

Repite el calculo de pares y segmentos variando dos decisiones del grupo:
  1. Como se ubica cada par en su quintil de valor (BASE_QUINTILES en src/tablas.py).
  2. A partir de cuantos dias entre ventas se anualiza el retorno (DIAS_MIN_ANUAL).

Uso (desde la raiz del proyecto, con data/ ya descargada):
    python -m src.sensibilidad

Salidas en reports/:
    sensibilidad_resumen.csv   una fila por combinacion (criterio x dias): pares, % de perdida,
                               mediana real y nominal, % de pares con perdida real, segmentos
                               reportables y que tanto se parece el ranking de segmentos al base.
    sensibilidad_segmentos.csv mediana real, intervalo y n de cada segmento en cada combinacion.

El caso base (nominal, 180 dias) debe reproducir la Tabla 10 y los 5.738 pares de la Guia 4.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from src import datos as D
    from src import tablas as T
except ImportError:
    import datos as D
    import tablas as T

CRITERIOS = ["nominal", "constantes", "segunda", "promedio"]
CORTES_DIAS = [30, 90, 180, 365]
BASE = ("nominal", 180)


def _rangos(serie: pd.Series) -> pd.Series:
    """Posicion 1..15 (1 = mayor retorno) de cada segmento."""
    return serie.rank(ascending=False, method="min")


def correr(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    resumen, detalle = [], []
    base_med = None
    n_base = None
    for crit in CRITERIOS:
        for dias in CORTES_DIAS:
            T.BASE_QUINTILES, T.DIAS_MIN_ANUAL = crit, dias
            pares, traza = T.construir_pares(df)
            seg = T.tabla_segmentos(pares)
            seg = seg.assign(criterio=crit, corte_dias=dias)
            detalle.append(seg)
            resumen.append({
                "criterio": crit, "corte_dias": dias, "pares": len(pares),
                "mediana_real_pct": round(100 * pares["ret_real"].median(), 2),
                "mediana_nominal_pct": round(100 * pares["ret_nominal"].median(), 2),
                "pct_pares_perdida_real": round(100 * (pares["ret_real"] < 0).mean(), 1),
                "segmentos_reportables": int(seg["suficiente"].sum()),
                "mayor_retorno": _extremo(seg, max),
                "menor_retorno": _extremo(seg, min),
                "pendiente_q1_q5": _pendiente(seg),
            })
    res = pd.DataFrame(resumen)
    det = pd.concat(detalle, ignore_index=True)
    # perdida de pares frente al caso base y similitud del ranking con el caso base
    n_base = res.loc[(res["criterio"] == BASE[0]) & (res["corte_dias"] == BASE[1]), "pares"].iloc[0]
    res["pares_vs_base_pct"] = (100 * (res["pares"] / n_base - 1)).round(1)
    b = det[(det["criterio"] == BASE[0]) & (det["corte_dias"] == BASE[1])].set_index(["zona", "q"])["mediana_real"]
    corr = {}
    for (c, d), g in det.groupby(["criterio", "corte_dias"]):
        m = g.set_index(["zona", "q"])["mediana_real"]
        corr[(c, d)] = round(float(_rangos(b).corr(_rangos(m.reindex(b.index)), method="pearson")), 3)
    # Spearman: 1 = mismo orden de los 15 segmentos. Se asigna por (criterio, corte), no por posicion.
    res["similitud_ranking_con_base"] = [corr[(c, d)] for c, d in zip(res["criterio"], res["corte_dias"])]
    return res, det


def _extremo(seg: pd.DataFrame, f) -> str:
    """Segmento con mayor o menor retorno entre los reportables (n >= 100); vacio si no hay ninguno."""
    ok = seg[seg["suficiente"]]
    if ok.empty:
        return ""
    v = ok["mediana_real"]
    return _etiqueta(seg, v.idxmax() if f is max else v.idxmin())


def _etiqueta(seg: pd.DataFrame, i) -> str:
    f = seg.loc[i]
    return f"{f['zona']} Q{int(f['q'])} ({100 * f['mediana_real']:.1f} %)"


def _pendiente(seg: pd.DataFrame) -> float:
    """Promedio por zona de (retorno Q5 - retorno Q1), en puntos porcentuales: negativo = el retorno baja al subir el rango."""
    p = seg.pivot(index="zona", columns="q", values="mediana_real")
    return round(float(100 * (p[5] - p[1]).mean()), 2)


def main() -> None:
    df = D.a_pesos_constantes(D.cargar_compraventas(), D.cargar_ipc())
    res, det = correr(df)
    Path("reports").mkdir(exist_ok=True)
    res.to_csv("reports/sensibilidad_resumen.csv", index=False)
    det.to_csv("reports/sensibilidad_segmentos.csv", index=False)
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
