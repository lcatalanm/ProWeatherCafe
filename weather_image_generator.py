import os
import base64
import requests
import json
from datetime import datetime, date, timedelta
from jinja2 import Template
from html2image import Html2Image
import sys

# === CONFIGURATION ===
LAT, LON = -21.1582019, 149.159265
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ OPENWEATHER_API_KEY is not defined.")

TEMPLATE_PATH   = "template.html"
LOGO_PATH       = "logobgc_vectorized.png"
ASSETS_DIR      = "background_images"
BG_FILENAME     = "Hotchocolate.jpg"
DEFAULT_BG      = "default.jpg"
OUTPUT_NAME     = f"{date.today().strftime('%Y-%m-%d')}_Mackay_Story.png"

# === HELPER FUNCTIONS ===
def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"⚠️ Image not found: {path}")
        # Try default background if specified one isn't found
        if path.endswith(BG_FILENAME) and os.path.exists(os.path.join(ASSETS_DIR, DEFAULT_BG)):
            print(f"Using default background instead.")
            return image_to_base64(os.path.join(ASSETS_DIR, DEFAULT_BG))
        return ""

def fetch_forecast():
    tomorrow = date.today() + timedelta(days=1)
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LAT}&lon={LON}"
        "&units=metric&lang=en"
        f"&appid={API_KEY}"
    )
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        print(f"⚠️ Error fetching weather data: {e}")
        sys.exit(1)

    # Extract forecasts for 9am and 12pm
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

# === MAIN PROCESS ===
try:
    date_str, forecasts = fetch_forecast()

    # Read template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tpl = Template(f.read())

    html = tpl.render(
        date=date_str,
        forecasts=forecasts,
        background_image=image_to_base64(os.path.join(ASSETS_DIR, BG_FILENAME)),
        logo_image=image_to_base64(LOGO_PATH)
    )

    # Save temporary HTML
    with open("rendered_template.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Generate image with html2image (uses Chrome headless)
    hti = Html2Image(
        output_path=".",
        custom_flags=[
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-software-rasterizer",
            "--hide-scrollbars",
            "--force-device-scale-factor=1"
        ]
    )
    
    # Generate the image
    hti.screenshot(
        html_file="rendered_template.html",
        save_as=OUTPUT_NAME,
        size=(1080, 1080)
    )

    # Verify image was created
    if os.path.exists(OUTPUT_NAME):
        file_size = os.path.getsize(OUTPUT_NAME)
        print(f"{file_size} bytes written to file {os.path.abspath(OUTPUT_NAME)}")
        print(f"✅ Imagen generada: {OUTPUT_NAME}")
        print(f"✅ Generated image: {OUTPUT_NAME}")
    else:
        print(f"⚠️ Failed to generate image: {OUTPUT_NAME}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error generating weather image: {e}")
    sys.exit(1)