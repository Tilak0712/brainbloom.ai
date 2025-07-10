import requests
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("HF_API_TOKEN")

def generate_image(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "image/png",
        "Content-Type": "application/json"
    }
    payload = {"inputs": prompt}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 503:
            return "⏳ Model is loading. Try again in a few seconds."
        if response.status_code == 404:
            return "❌ Error 404: Model not found."
        if response.status_code != 200:
            return f"❌ Error: {response.status_code} - {response.text}"

        return Image.open(BytesIO(response.content))

    except Exception as e:
        return f"❌ Failed to generate image: {e}"
