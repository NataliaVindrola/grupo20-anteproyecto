"""Figura de sensibilidad para el informe (retroalimentacion de la Guia 4).

Lee reports/sensibilidad_resumen.csv (lo genera `python -m src.sensibilidad`) y dibuja dos graficos:
  A. Caida del retorno real de Q1 (barato) a Q5 (caro) segun el criterio con que se ubica cada par en su quintil
     (corte de 180 dias). Si el patron fuera real no cambiaria tanto de un criterio a otro.
  B. Valorizacion real mediana anual segun el corte de dias para anualizar (criterio nominal de la 1a venta).

Uso (desde la raiz del repositorio):
    python -m src.figuras
Salida: reports/figuras/sensibilidad.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ENTRADA = Path("reports/sensibilidad_resumen.csv")
SALIDA = Path("reports/figuras/sensibilidad.png")

AZUL, NARANJA = "#2a78d6", "#eb6834"
TEXTO, SECUNDARIO, GRIS = "#0b0b0b", "#52514e", "#c9c8c3"
ETIQUETAS = {"nominal": "Valor nominal\n1.ª venta (base)", "constantes": "Valor real\n1.ª venta",
             "segunda": "Valor real\n2.ª venta", "promedio": "Valor real promedio\nde las dos ventas"}


def coma(x: float, dec: int = 1) -> str:
    return f"{x:+.{dec}f}".replace(".", ",").replace("-", "−")


def main() -> None:
    r = pd.read_csv(ENTRADA)
    plt.rcParams.update({"font.size": 12, "axes.edgecolor": GRIS, "axes.labelcolor": SECUNDARIO,
                         "xtick.color": SECUNDARIO, "ytick.color": SECUNDARIO})
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.1, 1]})

    # A. caida Q1 -> Q5 por criterio (corte 180)
    d = r[r["corte_dias"] == 180].set_index("criterio").loc[list(ETIQUETAS)]
    x = range(len(d))
    barras = a.bar(x, d["pendiente_q1_q5"], width=0.6, color=AZUL)
    a.axhline(0, color=SECUNDARIO, lw=1)
    for rect, v in zip(barras, d["pendiente_q1_q5"]):
        a.text(rect.get_x() + rect.get_width() / 2, v + (0.6 if v >= 0 else -0.6), coma(v),
               ha="center", va="bottom" if v >= 0 else "top", color=TEXTO, fontweight="bold")
    a.set_xticks(list(x), [ETIQUETAS[c] for c in d.index])
    a.set_ylim(-19, 6)
    a.set_ylabel("Cambio del retorno real de Q1 a Q5\n(puntos porcentuales, promedio de las 3 zonas)")
    a.set_title("A. El patrón depende de cómo se clasifica", loc="left", color=TEXTO, fontweight="bold")

    # B. mediana real segun el corte de dias (criterio nominal)
    n = r[r["criterio"] == "nominal"].sort_values("corte_dias").reset_index(drop=True)
    b.axhline(0, color=SECUNDARIO, lw=1)
    b.plot(range(len(n)), n["mediana_real_pct"], color=AZUL, lw=2, marker="o", ms=9, mfc=AZUL, mec="white", mew=2)
    for i, v in enumerate(n["mediana_real_pct"]):
        b.text(i + 0.1, v + 0.8, coma(v) + " %", ha="left", va="bottom", color=TEXTO, fontweight="bold")
    etiquetas = []
    for c, p in zip(n["corte_dias"], n["pares"]):
        t = f"{c} días" + (" (actual)" if c == 180 else "")
        etiquetas.append(t + "\n" + f"{p:,}".replace(",", ".") + " pares")
    b.set_xticks(range(len(n)), etiquetas)
    b.set_xlim(-0.4, len(n) - 0.2)
    b.set_ylim(-4.5, 16)
    b.set_ylabel("Valorización real mediana anual (%)")
    b.set_xlabel("Mínimo de días entre ventas para anualizar", color=SECUNDARIO)
    b.set_title("B. La cifra cambia con el corte de días", loc="left", color=TEXTO, fontweight="bold")

    for ax in (a, b):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#ecebe7", lw=0.8)
        ax.set_axisbelow(True)
    fig.text(0.01, 0.005, "Fuente: reports/sensibilidad_resumen.csv; cálculo del grupo 20 (5.738 pares en el caso base).",
             color=SECUNDARIO, fontsize=10)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=200, facecolor="white")
    print(SALIDA)


if __name__ == "__main__":
    main()
