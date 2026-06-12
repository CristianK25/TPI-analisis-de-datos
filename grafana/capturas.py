"""
capturas.py – Exporta cada panel del dashboard a PNG usando el image-renderer.

Requiere que el stack esté levantado (`docker compose up -d`) y que la base ya
tenga datos (`python src/load_db.py`). Llama al endpoint /render/d-solo de
Grafana (acceso anónimo Admin) y guarda un PNG por panel en docs/capturas/.

Uso:
    python grafana/capturas.py
"""

import os
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "docs", "capturas")
GRAFANA = os.getenv("GRAFANA_URL", "http://localhost:3000")
DASH_UID = "tpi-academico"
DASH_SLUG = "tpi-desempeno-academico-hito-3"

# (panelId, nombre de archivo, ancho, alto)
PANELES = [
    (1, "00_kpi_estudiantes", 500, 250),
    (2, "01_kpi_nota_final", 500, 250),
    (3, "02_kpi_asistencia", 500, 250),
    (4, "03_kpi_riesgo", 500, 250),
    (10, "04_P1_agotamiento", 1100, 600),
    (11, "05_P2_brecha_digital", 1100, 600),
    (12, "06_P3_comportamientos_atipicos", 1100, 600),
    (13, "07_riesgo_por_carrera", 1100, 600),
]


def esperar_grafana(reintentos=30, espera=3):
    for i in range(1, reintentos + 1):
        try:
            with urllib.request.urlopen(f"{GRAFANA}/api/health", timeout=5) as r:
                if r.status == 200:
                    print("[OK] Grafana responde.")
                    return True
        except Exception:
            pass
        print(f"[..] Esperando a Grafana ({i}/{reintentos})...")
        time.sleep(espera)
    return False


def render(panel_id, width, height):
    url = (
        f"{GRAFANA}/render/d-solo/{DASH_UID}/{DASH_SLUG}"
        f"?panelId={panel_id}&width={width}&height={height}"
        f"&theme=light&from=now-6h&to=now&tz=America%2FArgentina%2FBuenos_Aires"
    )
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Panel {panel_id}: la respuesta no es un PNG válido")
    return data


def render_dashboard_completo(width=1400, height=1000):
    """Captura del dashboard completo (todos los paneles en una imagen)."""
    url = (
        f"{GRAFANA}/render/d/{DASH_UID}/{DASH_SLUG}"
        f"?width={width}&height={height}&theme=light&from=now-6h&to=now"
        f"&tz=America%2FArgentina%2FBuenos_Aires&kiosk=true"
    )
    with urllib.request.urlopen(url, timeout=90) as r:
        data = r.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Dashboard completo: la respuesta no es un PNG válido")
    return data


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if not esperar_grafana():
        print("[ERROR] Grafana no respondió. ¿Está levantado el stack? (docker compose up -d)")
        return 1

    ok = 0
    for panel_id, nombre, w, h in PANELES:
        try:
            data = render(panel_id, w, h)
            ruta = os.path.join(OUT_DIR, f"{nombre}.png")
            with open(ruta, "wb") as f:
                f.write(data)
            print(f"[OK] Panel {panel_id:>2} -> {nombre}.png ({len(data) // 1024} KB)")
            ok += 1
        except Exception as e:
            print(f"[ERROR] Panel {panel_id}: {e}")

    # Captura del dashboard completo
    try:
        data = render_dashboard_completo()
        ruta = os.path.join(OUT_DIR, "08_dashboard_completo.png")
        with open(ruta, "wb") as f:
            f.write(data)
        print(f"[OK] Dashboard completo -> 08_dashboard_completo.png ({len(data) // 1024} KB)")
        ok += 1
    except Exception as e:
        print(f"[ERROR] Dashboard completo: {e}")

    print(f"\n[LISTO] {ok}/{len(PANELES) + 1} capturas guardadas en {OUT_DIR}")
    return 0 if ok == len(PANELES) + 1 else 2


if __name__ == "__main__":
    raise SystemExit(main())
