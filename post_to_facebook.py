import os
import requests

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
IMAGE_PATH = "output_forecast.png"
CAPTION_PATH = "beverage_recommendation.txt"
GRAPH_API_VERSION = "v17.0"

# === VALIDACIONES ===
if not ACCESS_TOKEN or not PAGE_ID:
    raise RuntimeError("❌ Deben estar definidas FB_ACCESS_TOKEN y FACEBOOK_PAGE_ID")

if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"❌ No se encontró la imagen: {IMAGE_PATH}")

if not os.path.exists(CAPTION_PATH):
    raise FileNotFoundError(f"❌ No se encontró el archivo de caption: {CAPTION_PATH}")

# === CARGAR TEXTO ===
with open(CAPTION_PATH, "r", encoding="utf-8") as f:
    caption = f.read()

# === HACER POST ===
url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PAGE_ID}/photos"
with open(IMAGE_PATH, "rb") as img:
    files = {"source": img}
    data = {
        "access_token": ACCESS_TOKEN,
        "caption": caption
    }
    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        print("✅ Publicación realizada correctamente.")
    except requests.RequestException as e:
        raise RuntimeError(f"❌ Error al publicar en Facebook: {e}")
