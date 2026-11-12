"""Valida la integridad de las tablas de diseño (data/design/). Se ejecuta en CI."""
import sys
from pathlib import Path

import pandas as pd

D = Path(__file__).resolve().parent.parent / "data" / "design"
TOL = 0.5  # los porcentajes están redondeados a 1 decimal
errores = []


def leer(nombre, columnas):
    df = pd.read_csv(D / nombre)
    faltan = set(columnas) - set(df.columns)
    if faltan:
        errores.append(f"{nombre}: faltan columnas {sorted(faltan)}")
    return df


def suma_100(df, col, nombre):
    total = df[col].sum()
    if abs(total - 100) > TOL:
        errores.append(f"{nombre}: {col} suma {total:.1f}, se esperaba 100")


sites = leer("sites.csv", ["sede", "nombre", "tipo"])
offices = leer("offices.csv", ["oficina_id", "sede", "marca", "peso_demanda_pct"])
cats = leer("categories.csv", ["categoria", "clases_acriss", "peso_demanda_pct", "tarifa_p10", "tarifa_mediana", "tarifa_p90"])
chans = leer("channels.csv", ["canal", "peso_reservas_pct"])
dow = leer("demand_profile_dow.csv", ["dia", "pct_recogidas"])
hour = leer("demand_profile_hour.csv", ["hora", "pct_recogidas"])

suma_100(offices, "peso_demanda_pct", "offices.csv")
suma_100(cats, "peso_demanda_pct", "categories.csv")
suma_100(chans, "peso_reservas_pct", "channels.csv")
suma_100(dow, "pct_recogidas", "demand_profile_dow.csv")
suma_100(hour, "pct_recogidas", "demand_profile_hour.csv")

if not set(offices["sede"]) <= set(sites["sede"]):
    errores.append("offices.csv: hay sedes que no existen en sites.csv")
if offices["oficina_id"].duplicated().any():
    errores.append("offices.csv: oficina_id duplicado")
if not ((cats["tarifa_p10"] <= cats["tarifa_mediana"]) & (cats["tarifa_mediana"] <= cats["tarifa_p90"])).all():
    errores.append("categories.csv: tarifas fuera de orden p10 <= mediana <= p90")

# Guardia de privacidad: ninguna tabla debe traer columnas con datos personales
prohibidas = {"nombre_cliente", "cliente", "n_reserva", "reserva", "email", "telefono", "cedula"}
for archivo in D.glob("*.csv"):
    cols = {c.lower() for c in pd.read_csv(archivo, nrows=0).columns}
    if cols & prohibidas:
        errores.append(f"{archivo.name}: columnas sospechosas {sorted(cols & prohibidas)}")

if errores:
    print("FALLÓ la validación:")
    for e in errores:
        print(" -", e)
    sys.exit(1)
print("OK: tablas de diseño válidas")
