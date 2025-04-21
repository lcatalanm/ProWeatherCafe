import os
import requests
from datetime import datetime, date, timedelta
from jinja2 import Environment, FileSystemLoader
from html2image import Html2Image
import base64

# === CONFIGURACIÓN ===
LAT, LON = -21.1582019, 149.159265
UNITS = "metric"
LANG = "en"
API_KEY = os.getenv("OPENWEATHER_API_KEY")
TEMPLATE = "template.html"
OUTPUT_IMAGE = "output_forecast.png"
ASSETS_DIR = "background_images"
LOGO_PATH = "logobgc_vectorized.png"
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "hotchocolate.jpg")

# === VALIDACIÓN DE VARIABLES DE ENTORNO ===
if not API_KEY:
    raise RuntimeError("❌ OPENWEATHER_API_KEY no está definida.")

# === FUNCIONES ===
def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"⚠️ Imagen no encontrada: {path}")
        return ""

def get_weather_forecast():
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={LAT}&lon={LON}&units={UNITS}&lang={LANG}&appid={API_KEY}"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"❌ Error al obtener pronóstico: {e}")

def get_forecast_for_hour(data, target_hour):
    tomorrow = date.today() + timedelta(days=1)
    forecasts = [item for item in data["list"]
                 if datetime.fromtimestamp(item["dt"]).date() == tomorrow]

    def closest(item):
        forecast_time = datetime.fromtimestamp(item["dt"]).time()
        return abs(datetime.combine(tomorrow, forecast_time).hour - target_hour)

    return min(forecasts, key=closest)

# === PROCESO PRINCIPAL ===
weather_data = get_weather_forecast()
forecast_9am = get_forecast_for_hour(weather_data, 9)
forecast_12pm = get_forecast_for_hour(weather_data, 12)

env = Environment(loader=FileSystemLoader("."))
template = env.get_template(TEMPLATE)

rendered_html = template.render(
    forecasts=[
        {
            "time": datetime.fromtimestamp(forecast_9am["dt"]).strftime("%I:%M %p"),
            "temp": f"{forecast_9am['main']['temp']}°C",
            "humidity": f"{forecast_9am['main']['humidity']}%"
        },
        {
            "time": datetime.fromtimestamp(forecast_12pm["dt"]).strftime("%I:%M %p"),
            "temp": f"{forecast_12pm['main']['temp']}°C",
            "humidity": f"{forecast_12pm['main']['humidity']}%"
        }
    ],
    date=date.today().strftime("%A, %d %B %Y"),
    logo_image=image_to_base64(LOGO_PATH),
    background_image=image_to_base64(BACKGROUND_PATH)
)


hti = Html2Image(output_path='.', custom_flags=['--virtual-time-budget=3000'])
hti.screenshot(html_str=rendered_html, save_as=OUTPUT_IMAGE)

print(f"✅ Imagen generada: {OUTPUT_IMAGE}")
