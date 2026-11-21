# Grupo 20 - Anteproyecto: segmentos del mercado de vivienda de Bogota

Gerencia de Proyectos de Analytics (MIAD). Integrantes: Natalia Vindrola, Jorge Alarcon, Julian Zapata, Juan Camilo Restrepo.

Este repositorio contiene **solo el codigo que genera las cifras de la Guia 4** (limpieza, pares de ventas repetidas,
valorizacion, liquidez y rango historico). No incluye modelos de prediccion ni tablero: eso pertenece al proyecto de despliegue.

## Contenido
- `src/limpieza.py`: reglas de limpieza (zona, fechas, valor >= $5 M, duplicados) y deflactacion. Genera `reports/limpieza_resumen.csv` (Tabla 5).
- `src/datos.py`: carga de datos y pesos constantes.
- `src/tablas.py`: pares de ventas repetidas, segmentos, liquidez (Kaplan-Meier) y rango historico. Genera `reports/pares_filtros.csv` (Tabla 6) y `reports/tablas/`.
- `src/sensibilidad.py`: repite la valorizacion con otras definiciones del rango de valor y otros cortes de dias (retroalimentacion de la Guia 4).
- `src/figuras.py`: figura de sensibilidad para el informe (`reports/figuras/sensibilidad.png`), a partir de `reports/sensibilidad_resumen.csv`.
- `data/*.dvc`: punteros a los datos (compraventas IGAC-SNR e IPC del DANE, base dic-2018 = 100).
- `reports/`: salidas de referencia de la Guia 4 (`limpieza_resumen.csv`, `pares_filtros.csv`).

## Reproducir (desde la raiz)
```
pip install -r requirements.txt
# colocar en data/ compraventas_0125_bogota.csv e ipc.csv (dvc pull desde el repositorio de despliegue, o copiarlos)
python src/limpieza.py            # Tabla 5  -> reports/limpieza_resumen.csv
python -m src.tablas              # Tabla 6  -> reports/pares_filtros.csv y reports/tablas/
python -m src.sensibilidad        # sensibilidad -> reports/sensibilidad_*.csv
python -m src.figuras             # figura -> reports/figuras/sensibilidad.png
```

## Que debe dar (Guia 4)
665.086 filas crudas -> 665.077 -> 664.051 ventas (duplicados: se conserva el mayor valor) -> 259.977 con valor valido;
pares 10.181 -> 10.036 -> 9.800 -> 9.332 -> 5.990 -> 5.738. El caso base de `sensibilidad.py` (nominal, 180 dias) debe dar 5.738 pares.
