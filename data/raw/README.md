# data/raw — solo local

Esta carpeta guarda los archivos reales (manifiestos de reservas, mapa de oficinas).
Todo su contenido está en `.gitignore`: **nunca se sube a GitHub**.

Para recalibrar el diseño:

1. Copia el manifiesto aquí (`manifest.xlsx`).
2. Copia `data/design/office_map.example.json` como `office_map.json` y pon los códigos reales de oficina.
3. Ejecuta `python scripts/calibrate_from_manifest.py data/raw/manifest.xlsx`.
