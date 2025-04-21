import os
import base64
import requests
import json
from datetime import datetime, date, timedelta
from jinja2 import Template
from html2image import Html2Image

# === CONFIGURACIÓN ===
LAT, LON = -21.1582019, 149.159265
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ OPENWEATHER_API_KEY no está definida.")

TEMPLATE_PATH   = "template.html"
LOGO_PATH       = "logobgc_vectorized.png"
ASSETS_DIR      = "background_images"
BG_FILENAME     = "Hotchocolate.jpg"
DEFAULT_BG      = "default.jpg"
OUTPUT_NAME     = f"{date.today().strftime('%Y-%m-%d')}_Mackay_Story.png"

# === FUNCIONES AUXILIARES ===
def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"⚠️ Imagen no encontrada: {path}")
        return ""

def fetch_forecast():
    tomorrow = date.today() + timedelta(days=1)
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LAT}&lon={LON}"
        "&units=metric&lang=en"
        f"&appid={API_KEY}"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    # Extraer pronósticos para 9am y 12pm
    def closest(hour):
        target = datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=hour)
        return min(
            (item for item in data["list"]
             if datetime.fromtimestamp(item["dt"]).date() == tomorrow),
            key=lambda x: abs(datetime.fromtimestamp(x["dt"]) - target),
            default=None
        )

    out = []
    for h in (9, 12):
        f = closest(h)
        if f:
            out.append({
                "time": datetime.fromtimestamp(f["dt"]).strftime("%I:%M %p").lstrip("0").lower(),
                "temp": f"{f['main']['temp']:.1f}°C",
                "humidity": f"{f['main']['humidity']}%"
            })
        else:
            out.append({"time": f"{h}:00", "temp": "N/A", "humidity": "N/A"})
    return tomorrow.strftime("%A, %B %d, %Y"), out

# === PROCESO PRINCIPAL ===
date_str, forecasts = fetch_forecast()

# Leer plantilla
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    tpl = Template(f.read())

html = tpl.render(
    date=date_str,
    forecasts=forecasts,
    background_image=image_to_base64(os.path.join(ASSETS_DIR, BG_FILENAME)),
    logo_image=image_to_base64(LOGO_PATH)
)

# Guardar HTML temporal
with open("rendered_template.html", "w", encoding="utf-8") as f:
    f.write(html)

# Generar imagen con html2image (usa Chrome headless)
hti = Html2Image(
    output_path=".",
    custom_flags=[
        "--headless=new",
        "--no-sandbox",
        "--hide-scrollbars",
        "--force-device-scale-factor=1"
    ]
)
hti.screenshot(
    html_file="rendered_template.html",
    save_as=OUTPUT_NAME,
    size=(1080, 1080)
)

print(f"✅ Imagen generada: {OUTPUT_NAME}")
