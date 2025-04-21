import os
import requests
from datetime import datetime

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
PAGE_ID      = os.getenv("FACEBOOK_PAGE_ID")
IMAGE_PATH   = f"{datetime.now().strftime('%Y-%m-%d')}_Mackay_Story.png"
CAPTION_PATH = "beverage_recommendation.txt"
API_VERSION  = "v17.0"

# — Validaciones —
if not ACCESS_TOKEN or not PAGE_ID:
    raise RuntimeError("❌ Falta definir FB_ACCESS_TOKEN o FACEBOOK_PAGE_ID")
if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"❌ No se encontró la imagen: {IMAGE_PATH}")
if not os.path.exists(CAPTION_PATH):
    raise FileNotFoundError(f"❌ No se encontró el caption: {CAPTION_PATH}")

# — Leer caption —
with open(CAPTION_PATH, "r", encoding="utf-8") as f:
    caption = f.read().strip()

# — Publicar en Facebook —
url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/photos"
with open(IMAGE_PATH, "rb") as img:
    files = {"source": img}
    data = {"access_token": ACCESS_TOKEN, "caption": caption}

    resp = requests.post(url, files=files, data=data)
    try:
        resp.raise_for_status()
        print("✅ Publicación realizada correctamente.")
    except requests.RequestException as e:
        print("❌ Error al publicar:", resp.text)
        raise
