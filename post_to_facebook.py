import os
import requests
import json
import sys
from datetime import datetime

# Constants
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
PAGE_ID      = os.getenv("FACEBOOK_PAGE_ID")
IMAGE_PATH   = f"{datetime.now().strftime('%Y-%m-%d')}_Mackay_Story.png"
CAPTION_PATH = "beverage_recommendation.txt"
API_VERSION  = "v17.0"

def validate_token():
    """Pre-validate the Facebook token before attempting to post"""
    if not ACCESS_TOKEN:
        print("❌ Missing FB_ACCESS_TOKEN environment variable")
        return False
    
    # Validate token with Facebook API
    validate_url = f"https://graph.facebook.com/{API_VERSION}/debug_token"
    params = {
        "input_token": ACCESS_TOKEN,
        "access_token": ACCESS_TOKEN
    }
    
    try:
        r = requests.get(validate_url, params=params, timeout=30)
        data = r.json()
        
        # Check if token is valid
        if "data" in data and data["data"].get("is_valid", False):
            print("✅ Facebook token is valid")
            return True
        else:
            print(f"❌ Facebook token validation failed: {json.dumps(data)}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error validating Facebook token: {e}")
        return False

def main():
    # — Validations —
    if not ACCESS_TOKEN or not PAGE_ID:
        raise RuntimeError("❌ Missing FB_ACCESS_TOKEN or FACEBOOK_PAGE_ID")
    
    if not os.path.exists(IMAGE_PATH):
        raise FileNotFoundError(f"❌ Image not found: {IMAGE_PATH}")
    
    if not os.path.exists(CAPTION_PATH):
        raise FileNotFoundError(f"❌ Caption file not found: {CAPTION_PATH}")
    
    # Validate token first
    if not validate_token():
        raise RuntimeError("❌ Facebook token is invalid or expired. Please generate a new token.")
    
    # — Read caption —
    with open(CAPTION_PATH, "r", encoding="utf-8") as f:
        caption = f.read().strip()
    
    # — Post to Facebook —
    url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/photos"
    
    # Verify image size and existence
    file_size = os.path.getsize(IMAGE_PATH)
    print(f"Image size: {file_size} bytes")
    
    with open(IMAGE_PATH, "rb") as img:
        files = {"source": img}
        data = {"access_token": ACCESS_TOKEN, "caption": caption}
        
        try:
            print(f"Posting to Facebook page ID: {PAGE_ID}")
            resp = requests.post(url, files=files, data=data, timeout=60)
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ Successfully posted to Facebook. Post ID: {result.get('id', 'unknown')}")
                print(f"✅ Publicación realizada correctamente.")
                return True
            else:
                print(f"❌ Error posting to Facebook: {resp.status_code}")
                print(f"Response: {resp.text}")
                raise requests.RequestException(f"Failed to post to Facebook: {resp.text}")
        except requests.RequestException as e:
            print(f"❌ Error al publicar: {e}")
            raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)