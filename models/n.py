import requests
import os

api_key = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://yourdomain.com",  # Optional
    "X-Title": "BrainBloom AI"
}

data = {
    "model": "meta-llama/Meta-Llama-3-8B-Instruct",
    "messages": [{"role": "user", "content": "Hello, who are you?"}]
}

response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
print(response.status_code)
print(response.json())
