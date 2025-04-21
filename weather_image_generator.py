import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURACIÓN ---
BACKGROUND_IMAGE = "background_images/Hotchocolate.jpg"
DEFAULT_BACKGROUND = "background_images/default.jpg"
OUTPUT_IMAGE_NAME = f"{datetime.now().strftime('%Y-%m-%d')}_Mackay_Story.png"

# --- FUNCIÓN PARA CARGAR IMAGEN DE FONDO ---
def load_background():
    if os.path.exists(BACKGROUND_IMAGE):
        return Image.open(BACKGROUND_IMAGE)
    elif os.path.exists(DEFAULT_BACKGROUND):
        print(f"⚠️ Imagen '{BACKGROUND_IMAGE}' no encontrada. Usando fondo por defecto.")
        return Image.open(DEFAULT_BACKGROUND)
    else:
        raise FileNotFoundError("❌ No hay ninguna imagen de fondo disponible.")

# --- GENERACIÓN DE LA IMAGEN ---
def generate_image():
    # Cargar imagen de fondo
    background = load_background().convert("RGBA")

    # Crear capa para texto
    txt_layer = Image.new("RGBA", background.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt_layer)

    # Fuente (puedes cambiar la ruta si es necesario)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 60)

    # Texto de ejemplo
    text = "🌞 Mackay Weather Today"
    w, h = draw.textsize(text, font=font)
    position = ((background.width - w) // 2, 100)
    
    # Contorno blanco
    outline_range = 2
    for x in range(-outline_range, outline_range + 1):
        for y in range(-outline_range, outline_range + 1):
            draw.text((position[0] + x, position[1] + y), text, font=font, fill="white")

    # Texto negro encima
    draw.text(position, text, font=font, fill="black")

    # Combinar capas
    final_image = Image.alpha_composite(background, txt_layer)
    final_image.convert("RGB").save(OUTPUT_IMAGE_NAME)
    print(f"✅ Imagen generada: {OUTPUT_IMAGE_NAME}")

# --- SI USA HTML Y SELENIUM (opcional) ---
def render_with_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Modo headless moderno
    chrome_options.add_argument("--window-size=1080,1920")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("file://" + os.path.abspath("weather_template.html"))

    screenshot_path = OUTPUT_IMAGE_NAME
    driver.save_screenshot(screenshot_path)
    driver.quit()
    print(f"✅ Captura guardada: {screenshot_path}")

# --- EJECUTAR ---
if __name__ == "__main__":
    try:
        generate_image()  # O usa render_with_selenium() si tu generación es vía HTML
    except Exception as e:
        print(f"❌ Error: {e}")
