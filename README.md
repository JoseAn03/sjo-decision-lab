# SJO Decision Lab

Sistema de decisiones para una rentadora de autos con operación en el Aeropuerto Internacional Juan Santamaría (SJO) y Belén, Costa Rica.

La operación es **100% sintética**, calibrada con estadísticas agregadas y datos públicos de turismo. No contiene datos personales ni registros reales de ninguna empresa.

## ¿Qué decisiones apoya?

- **Precio dinámico** por categoría, sede y anticipación
- **Redistribución de flota** entre SJO y Belén (one-way y pico de fin de semana)
- **Sobreventa y no-show** por categoría
- **Upgrades y sustituciones** cuando falta una categoría

## La operación en una tabla

| | |
|---|---|
| Sedes | SJO aeropuerto y Belén |
| Oficinas | 6 (2 sedes × 3 marcas) |
| Categorías de auto | 8 |
| Canales de reserva | 3 |

Detalle completo en [`docs/01-diseno-operacion.md`](docs/01-diseno-operacion.md).

## Misiones

El proyecto avanza en 14 misiones; cada una se completa solo cuando existe su entregable. Estado en [`missions/README.md`](missions/README.md).

| # | Misión | Estado |
|---|---|---|
| 1 | Diseñar la operación | ✅ |
| 2–14 | Por definir | ⬜ |

## Estructura

```
sjo-decision-lab/
├── docs/                # documentos de diseño por misión
├── data/
│   ├── design/          # tablas agregadas y versionadas
│   └── raw/             # solo local, en .gitignore
├── scripts/             # calibración y validación
├── missions/            # estado de las 14 misiones
└── .github/workflows/   # CI
```

## Cómo reproducir

```bash
pip install -r requirements.txt
python scripts/validate_design.py                       # valida las tablas
python scripts/calibrate_from_manifest.py data/raw/manifest.xlsx   # recalibra (datos locales)
```

## Privacidad

Los manifiestos reales nunca se versionan (`data/raw/` está en `.gitignore`). Los identificadores de oficina y de marca son genéricos y las tablas son agregados redondeados que no permiten reconstruir una reserva.

## Licencia

[MIT](LICENSE)
