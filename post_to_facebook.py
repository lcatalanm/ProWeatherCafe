import os
import requests
from datetime import date
import random

def get_creative_text(beverage_recommendation):
    texts = [
        "☀️ Rise and shine, Mackay! Here's your daily dose of weather and coffee inspiration. ☕",
        "🌤 Weather forecast with a side of caffeine! Check out what's brewing at Mackay Botanic Gardens today.",
        "🌿 Nature, weather, and coffee - the perfect trio! See what's in store for you today at our garden café.",
        "🌺 Blooming beautiful day ahead! Discover the perfect weather for a garden stroll and a cuppa.",
        "🍃 From gentle breezes to steaming brews, here's your daily Mackay Botanic Gardens update!",
        "🌸 Perk up your day with our weather report and beverage recommendation!",
        "🌴 Tropical vibes and coffee jives! Your daily Mackay weather and café update is here.",
        "🌻 Sunshine or showers? Either way, we've got the perfect drink waiting for you!",
        "🍵 Steep yourself in today's weather and our tailored drink recommendation.",
        "🌈 Whatever the weather, we've got you covered! Check out today's forecast and café special."
    ]
    chosen_text = random.choice(texts)
    return f"{chosen_text}\n\n{beverage_recommendation}"

def post_to_facebook(image_path, beverage_recommendation):
    access_token = os.environ.get("FB_ACCESS_TOKEN")
    page_id = os.environ.get("FACEBOOK_PAGE_ID")  # Usando el nuevo secreto

    url = f"https://graph.facebook.com/{page_id}/photos"

    message = get_creative_text(beverage_recommendation)

    with open(image_path, "rb") as image_file:
        params = {
            "access_token": access_token,
            "message": message
        }
        files = {
            "source": image_file
        }
        response = requests.post(url, params=params, files=files)

    if response.status_code == 200:
        print("Image posted successfully!")
    else:
        print(f"Failed to post image. Status code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    today = date.today().strftime("%Y-%m-%d")
    image_path = f"{today}_Mackay_Story.png"
    
    if os.path.exists(image_path):
        with open("beverage_recommendation.txt", "r") as f:
            beverage_recommendation = f.read().strip()
        post_to_facebook(image_path, beverage_recommendation)
    else:
        print("No image generated for today. Skipping Facebook post.")