import requests
import json
import base64
from datetime import date, datetime, timedelta
from jinja2 import Template
from html2image import Html2Image

# Configuración
api_key = "26b68d1690cad1a73037ef81ced8529b"  # Actualiza con tu API key
horarios = ["09:00:00", "10:00:00", "11:00:00", "12:00:00", "13:00:00", "14:00:00"]
city = "Mackay"

# Obtener datos del clima
url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
response = requests.get(url)
data = json.loads(response.text)

# Procesar datos del clima
forecasts = []
tomorrow = date.today()
for horario in horarios:
    forecast_time = datetime.combine(tomorrow, datetime.strptime(horario, "%H:%M:%S").time())
    forecast_found = False
    for forecast in data['list']:
        api_time = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
        if api_time.date() == tomorrow and abs(api_time - forecast_time) <= timedelta(hours=1):
            forecast_found = True
            forecasts.append({
                'time': forecast_time.strftime("%I:%M %p").lower().lstrip('0'),
                'temp': f"{forecast['main']['temp']:.1f}°C",
                'humidity': f"{forecast['main']['humidity']}%"
            })
            print(f"Encontrado pronóstico para {horario}: {forecast['dt_txt']}")
            break
    if not forecast_found:
        nearest_forecast = min(data['list'], key=lambda x: abs(datetime.strptime(x['dt_txt'], "%Y-%m-%d %H:%M:%S") - forecast_time))
        nearest_time = datetime.strptime(nearest_forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
        if nearest_time.date() == tomorrow:
            forecasts.append({
                'time': forecast_time.strftime("%I:%M %p").lower().lstrip('0'),
                'temp': f"{nearest_forecast['main']['temp']:.1f}°C",
                'humidity': f"{nearest_forecast['main']['humidity']}%"
            })
            print(f"Usando pronóstico más cercano para {horario}: {nearest_forecast['dt_txt']}")
        else:
            forecasts.append({
                'time': forecast_time.strftime("%I:%M %p").lower().lstrip('0'),
                'temp': 'N/A',
                'humidity': 'N/A'
            })
            print(f"No se encontró pronóstico para {horario}")

# Imprimir pronósticos procesados
print("\nPronósticos procesados:")
for forecast in forecasts:
    print(forecast)

# Convertir imágenes a base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

background_image = image_to_base64("background_images/hotchocolate.jpg")
logo_image = image_to_base64("logobgc_vectorized.png")

# Rellenar la plantilla HTML
with open("template.html") as file:
    template = Template(file.read())

rendered_html = template.render(
    date=(tomorrow).strftime("%A, %B %d, %Y"),
    forecasts=forecasts,
    background_image=background_image,
    logo_image=logo_image
)

# Guardar HTML renderizado
with open("rendered_template.html", "w") as file:
    file.write(rendered_html)

# Convertir HTML a imagen usando html2image
hti = Html2Image(output_path='.', custom_flags=['--no-sandbox', '--hide-scrollbars', '--force-device-scale-factor=1'])
hti = Html2Image(output_path='.')
hti.screenshot(html_file='rendered_template.html', save_as=f"{tomorrow}_Mackay_Story.png", size=(1080, 1080))
