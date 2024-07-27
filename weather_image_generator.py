import requests
import json
import base64
from datetime import date, datetime
from jinja2 import Template
from html2image import Html2Image
import os
import random

# ========================
# CONFIGURACIÓN
# ========================

api_key = os.environ.get("OPENWEATHER_API_KEY")
city = "West Mackay"

# ========================
# FUNCIONES AUXILIARES
# ========================

def is_cafe_open():
    """
    Determina si el café está abierto basado en el día de la semana.
    Retorna False los lunes y martes, True para el resto de días.
    """
    today = date.today().weekday()
    return today not in [0, 1]  # Cerrado lunes (0) y martes (1)

def select_background_image(temp_value):
    """
    Selecciona una imagen de fondo basada en la temperatura y el historial de uso.
    
    Args:
    temp_value (float): Temperatura actual.

    Returns:
    str: Ruta de la imagen seleccionada.
    """
    image_folder = "background_images"
    hot_images = ["egg_benedic.jpg", "chocolate_frappe.jpg", "Ice_coffe.jpg", "Sandwich in a sunny day.jpg"]
    cold_images = ["High_tea.jpg", "Stickydate pudding.jpg", "Hotchocolate.jpg"]
    neutral_images = ["Breakfast in a sunny day.jpg", "Club Sandwich.jpg", "Breakfast(eggs, bread).jpg", "Muffins.jpg", "Capuccino.jpg"]
    used_images_file = "used_images.json"

    # Cargar historial de imágenes usadas
    try:
        if os.path.exists(used_images_file):
            with open(used_images_file, "r") as f:
                content = f.read().strip()
                used_images = json.loads(content) if content else {}
        else:
            used_images = {}
    except json.JSONDecodeError:
        print("Error decodificando JSON. Reiniciando used_images.")
        used_images = {}

    current_week = date.today().isocalendar()[1]

    # Seleccionar conjunto de imágenes basado en la temperatura
    if temp_value > 25:
        available_images = [img for img in hot_images if used_images.get(img, 0) != current_week]
    elif temp_value < 15:
        available_images = [img for img in cold_images if used_images.get(img, 0) != current_week]
    else:
        available_images = [img for img in neutral_images if used_images.get(img, 0) != current_week]

    # Si no hay imágenes disponibles, usar todas
    if not available_images:
        available_images = hot_images + cold_images + neutral_images

    # Seleccionar y registrar imagen usada
    selected_image = random.choice(available_images)
    used_images[selected_image] = current_week

    # Guardar historial actualizado
    with open(used_images_file, "w") as f:
        json.dump(used_images, f)

    return os.path.join(image_folder, selected_image)

def image_to_base64(image_path):
    """
    Convierte una imagen a su representación en base64.
    
    Args:
    image_path (str): Ruta de la imagen.

    Returns:
    str: Representación en base64 de la imagen.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# ========================
# FUNCIÓN PRINCIPAL
# ========================

def generate_weather_image():
    """
    Genera una imagen con información del clima para el café.

    Returns:
    tuple: (nombre_archivo, recomendación_bebida) o (None, None) si el café está cerrado.
    """
    if not is_cafe_open():
        return None, None

    # Obtener datos del clima
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = json.loads(response.text)

    temp = f"{data['main']['temp']:.1f}°C"
    humidity = f"{data['main']['humidity']}%"
    condition = data['weather'][0]['description'].capitalize()
    temp_value = float(temp[:-2])

    # Generar recomendación de bebida
    if temp_value > 25:
        beverage_recommendation = "Beat the heat with our refreshing iced coffee!"
    elif temp_value < 15:
        beverage_recommendation = "Warm up with our delicious hot chocolate!"
    else:
        beverage_recommendation = "Perfect weather for any of our signature drinks!"

    # Seleccionar imagen de fondo
    background_image = select_background_image(temp_value)

    # Convertir imágenes a base64
    background_image_b64 = image_to_base64(background_image)
    logo_image_b64 = image_to_base64("logobgc_vectorized.png")

    # Rellenar la plantilla HTML
    with open("template.html") as file:
        template = Template(file.read())
    
    rendered_html = template.render(
        date=date.today().strftime("%A, %B %d, %Y"),
        temp=temp,
        humidity=humidity,
        condition=condition,
        beverage_recommendation=beverage_recommendation,
        background_image=background_image_b64,
        logo_image=logo_image_b64
    )

    # Guardar HTML renderizado
    with open("rendered_template.html", "w") as file:
        file.write(rendered_html)

    # Convertir HTML a imagen
    hti = Html2Image(output_path='.', custom_flags=['--no-sandbox', '--hide-scrollbars', '--force-device-scale-factor=1'])
    output_file = f"{date.today()}_Mackay_Story.png"
    hti.screenshot(html_file='rendered_template.html', save_as=output_file, size=(1080, 1080))

    return output_file, beverage_recommendation

# ========================
# EJECUCIÓN PRINCIPAL
# ========================

if __name__ == "__main__":
    output_file, beverage_recommendation = generate_weather_image()
    if output_file:
        print(f"Imagen generada: {output_file}")
        print(f"Recomendación de bebida: {beverage_recommendation}")
    else:
        print("Café cerrado hoy, no se generó imagen.")