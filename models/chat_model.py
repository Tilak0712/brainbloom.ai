import requests
import os
from dotenv import load_dotenv
from models.math_tool import solve_math
from models.pdf_tool import extract_text_from_pdf
from models.image_caption import describe_image
from models.diet_tool import diet_recommendation

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_web(query):
    try:
        res = requests.get("https://serpapi.com/search", params={
            "q": query,
            "engine": "duckduckgo",
            "api_key": SERPAPI_KEY
        })
        res.raise_for_status()
        results = res.json()
        if "organic_results" in results and len(results["organic_results"]) > 0:
            return "\n".join([
                f"- {r.get('title', 'No title')}: {r.get('link', '')}"
                for r in results["organic_results"][:3]
            ])
        return "No web search results found."
    except Exception as e:
        return f"Web search failed: {e}"

def detect_tool(user_text):
    text = user_text.lower()
    if any(op in text for op in ["+", "-", "*", "/", "solve", "calculate", "evaluate"]):
        return "math"
    if "pdf" in text or "read document" in text or "file" in text:
        return "pdf"
    if "describe image" in text or "what is in the image" in text:
        return "image"
    if "diet" in text or "calorie" in text or "meal plan" in text:
        return "diet"
    return None

def get_chat_response(user_input, uploaded_file=None, uploaded_image=None):
    try:
        user_text = user_input[-1]["content"] if isinstance(user_input, list) else user_input

        # ✅ Custom hardcoded responses
        lowered = user_text.lower().strip()
        if "who is your owner" in lowered or "who made you" in lowered or "who created you" in lowered:
            return "My owner is Mr. Tilak Lakhani. His father is Mahesh Lakhani and mother is Manisha Lakhani."

        tool = detect_tool(user_text)
        if tool == "math":
            return solve_math(user_text)
        elif tool == "pdf" and uploaded_file:
            return extract_text_from_pdf(uploaded_file)
        elif tool == "image" and uploaded_image:
            return describe_image(uploaded_image)
        elif tool == "diet":
            return diet_recommendation(user_text)

        realtime_keywords = [
            "current", "latest", "live", "today", "search", "google", "news",
            "price", "weather", "temperature", "time in", "who is", "what is",
            "who won", "cm of", "pm of", "ceo of"
        ]
        force_web = any(word in user_text.lower() for word in realtime_keywords)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "X-Title": "BrainBloom AI"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are BrainBloom AI, a powerful assistant with real-time tools, logic, creativity, and internet access. Answer anything smartly."},
                {"role": "user", "content": user_text}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"].strip()

        fallback_phrases = [
            "i don't know",
            "i'm not sure",
            "as of my last update",
            "i cannot provide real-time information",
            "i don't have real-time access"
        ]

        if any(phrase in ai_reply.lower() for phrase in fallback_phrases) or force_web:
            web_result = search_web(user_text)
            return f"BrainBloom AI Answer:\n{ai_reply}\n\nReal-Time Info:\n{web_result}"

        return ai_reply

    except Exception as e:
        return f"Error: {e}"
