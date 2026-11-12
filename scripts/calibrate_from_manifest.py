"""Calibra el diseño de la operación a partir de un manifiesto semanal de reservas.

USO (local; los archivos reales NUNCA se suben al repositorio):
    python scripts/calibrate_from_manifest.py data/raw/manifest.xlsx [data/raw/office_map.json]

El mapa de oficinas (código real -> sede y marca genérica) vive en data/raw/,
que está en .gitignore. Ver data/design/office_map.example.json.

Salida: tablas AGREGADAS en data/design/ (porcentajes y medianas redondeadas).
No se escribe ningún nombre, número de reserva ni dato personal.
"""
import json
import sys
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "design"

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MAP = ROOT / "data" / "raw" / "office_map.json"
BRANDS = {"Alamo", "Enterprise", "National"}  # valores del campo "Reservado por" que son la marca (canal directo)


def categoria(clase: str) -> str:
    """Agrupa el código ACRISS (46 clases) en 8 categorías sintéticas."""
    size, tipo = clase[0], clase[1]
    if tipo in "VK":
        return "VAN"
    if tipo == "J":
        return "4X4_JEEP"
    if tipo in "PQ":
        return "SUV_GRANDE"  # pickups: muy pocas, se funden con la categoría grande
    if tipo in "FGR":
        return {"E": "SUV_COMPACTO", "C": "SUV_COMPACTO", "M": "SUV_COMPACTO",
                "I": "SUV_INTERMEDIO", "S": "SUV_ESTANDAR",
                "F": "SUV_GRANDE"}.get(size, "SUV_PREMIUM")
    return "AUTO"


def canal(row) -> str:
    if pd.notna(row["Agencia de recom."]):
        return "AGENCIA"
    if row["Reservado por"] in BRANDS:
        return "MARCA_DIRECTO"
    return "AGENTE_MOSTRADOR"


def main(path: str, map_path: Path = DEFAULT_MAP) -> None:
    # {"codigo_real": ["SEDE", "OFICINA_ID", "MARCA_ID"]}
    offices = json.loads(Path(map_path).read_text(encoding="utf-8"))
    df = pd.read_excel(path)
    df.columns = [str(c).strip() for c in df.columns]
    df = df[~df["Nombre"].astype(str).str.contains("TEST", na=False)].copy()  # registros de prueba

    f = "%d/%m/%Y %H:%M"
    df["rec"] = pd.to_datetime(df["Fecha recogida"], format=f)
    df["ent"] = pd.to_datetime(df["Fecha entrega"], format=f)
    df["res"] = pd.to_datetime(df["Fecha de reserva"], format=f)
    df["dias"] = (df["ent"] - df["rec"]).dt.total_seconds() / 86400
    df["lead"] = (df["rec"] - df["res"]).dt.total_seconds() / 86400
    df["tarifa"] = pd.to_numeric(df["Tarifa diaria"], errors="coerce")
    df["cat"] = df["Clase"].map(categoria)
    df["canal"] = df.apply(canal, axis=1)
    df["one_way"] = df["Ubic. rec."] != df["Ubic. ent."]
    n = len(df)

    # 1) Oficinas
    rows = []
    for code, (sede, oficina_id, marca) in offices.items():
        g = df[df["Ubic. rec."] == code]
        rows.append({
            "oficina_id": oficina_id, "sede": sede, "marca": marca,
            "peso_demanda_pct": round(100 * len(g) / n, 1),
            "duracion_mediana_dias": round(g["dias"].median(), 1),
            "anticipacion_mediana_dias": round(g["lead"].median()),
            "tarifa_diaria_mediana": round(g["tarifa"].median()),
            "pct_one_way": round(100 * g["one_way"].mean(), 1),
        })
    pd.DataFrame(rows).to_csv(OUT / "offices.csv", index=False)

    # 2) Categorías
    cats = []
    for c, g in df.groupby("cat"):
        cats.append({
            "categoria": c,
            "clases_acriss": " ".join(sorted(g["Clase"].unique())),
            "peso_demanda_pct": round(100 * len(g) / n, 1),
            "tarifa_p10": round(g["tarifa"].quantile(0.10)),
            "tarifa_mediana": round(g["tarifa"].median()),
            "tarifa_p90": round(g["tarifa"].quantile(0.90)),
            "duracion_mediana_dias": round(g["dias"].median(), 1),
        })
    pd.DataFrame(cats).sort_values("peso_demanda_pct", ascending=False).to_csv(
        OUT / "categories.csv", index=False)

    # 3) Canales
    chs = []
    for c, g in df.groupby("canal"):
        chs.append({
            "canal": c,
            "peso_reservas_pct": round(100 * len(g) / n, 1),
            "anticipacion_mediana_dias": round(g["lead"].median()),
            "tarifa_diaria_mediana": round(g["tarifa"].median()),
            "duracion_mediana_dias": round(g["dias"].median(), 1),
            "pct_con_vuelo": round(100 * g["Nº de vuelo"].notna().mean(), 1),
        })
    pd.DataFrame(chs).sort_values("peso_reservas_pct", ascending=False).to_csv(
        OUT / "channels.csv", index=False)

    # 4) Perfil de demanda (una sola semana: referencia, no estacionalidad)
    dow = df["rec"].dt.dayofweek.value_counts(normalize=True).sort_index() * 100
    nombres = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    pd.DataFrame({"dia": nombres, "pct_recogidas": dow.round(1).values}).to_csv(
        OUT / "demand_profile_dow.csv", index=False)
    hr = (df["rec"].dt.hour.value_counts(normalize=True).sort_index() * 100).round(1)
    hr.rename_axis("hora").rename("pct_recogidas").reset_index().to_csv(
        OUT / "demand_profile_hour.csv", index=False)

    print(f"OK: {n} reservas agregadas -> {OUT}")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(sys.argv[1], Path(sys.argv[2]) if len(sys.argv) == 3 else DEFAULT_MAP)
