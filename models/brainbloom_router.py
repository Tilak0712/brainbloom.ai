import re
from models.chat_model import get_chat_response
from models.image_gen import generate_image as gen_img

def ai_chat(prompt):
    reply, _ = get_chat_response([
        {"role": "system", "content": "You are BrainBloom AI."},
        {"role": "user", "content": prompt}
    ], model="gryphe/mythomax-l2-13b")
    return {"type": "chat", "response": reply}

def generate_image(prompt):
    img = gen_img(prompt)
    if img:
        return {"type": "image", "response": "[Image Generated]", "image": img}
    return {"type": "image", "response": "❌ Failed to generate image."}

def handle_pdf_question(prompt):
    return {"type": "pdf", "response": f"[PDF Tool Placeholder] {prompt}"}

def generate_diet_plan(prompt):
    goal = "balanced"
    if "gain" in prompt.lower():
        goal = "weight gain"
    elif "lose" in prompt.lower() or "fat" in prompt.lower():
        goal = "weight loss"
    return {"type": "diet", "response": f"🍽️ Sample {goal} meal plan:\n- Breakfast: Oats with fruits\n- Lunch: Rice, dal, vegetables\n- Dinner: Paneer/tofu with roti\n- Snacks: Nuts, smoothie"}

def generate_bhajan(prompt):
    return {"type": "bhajan", "response": "🙏 Swaminarayan Bhajan:\n\n\"Jai Swaminarayan, dayalu tamé,\nBhakto par kari dayalu...\""}

def generate_quote_poster(prompt):
    return {"type": "poster", "response": f"🖼️ Inspirational Quote: \"{prompt}\""}

def do_web_search(prompt):
    return {"type": "web", "response": f"🌐 Searching web for: {prompt}\n[Web Search Placeholder]"}

def fallback_response(prompt):
    return {"type": "unknown", "response": f"🤖 I’m still learning how to answer: {prompt}"}

def is_math_expression(text):
    return bool(re.fullmatch(r"[0-9\.\*\+\-/\s\(\)]+", text.strip()))

def solve_math_expression(expression):
    try:
        result = eval(expression)
        return {"type": "math", "response": f"🧮 Answer: {result}"}
    except Exception as e:
        return {"type": "math", "response": f"❌ Math Error: {e}"}

def detect_intent(text):
    text = text.lower()
    if is_math_expression(text):
        return "math"
    elif re.search(r"\b(draw|generate image|cartoon|poster|make a poster)\b", text):
        return "image"
    elif re.search(r"\b(pdf|document|file|upload)\b", text):
        return "pdf"
    elif re.search(r"\b(diet|meal|eat|fat|gain|lose weight)\b", text):
        return "diet"
    elif re.search(r"\b(bhajan|sing|swaminarayan|prayer)\b", text):
        return "bhajan"
    elif re.search(r"\b(quote|inspire|motivation|thought)\b", text):
        return "poster"
    elif re.search(r"\b(who is|what is|news|latest|from internet)\b", text):
        return "web"
    else:
        return "chat"

def smart_router(user_input):
    intent = detect_intent(user_input)

    if len(user_input.strip()) < 3 or user_input.lower() in ["ok", "do it", "yes", "no", "this", "that"]:
        return {"type": "chat", "response": "Could you please clarify what you meant?"}

    tool_map = {
        "math": solve_math_expression,
        "image": generate_image,
        "pdf": handle_pdf_question,
        "diet": generate_diet_plan,
        "bhajan": generate_bhajan,
        "poster": generate_quote_poster,
        "web": do_web_search,
        "chat": ai_chat
    }

    result = tool_map.get(intent, fallback_response)(user_input)

    if result["type"] == "image":
        result["response"] += "\n\n🖼️ Would you like me to describe something specific in this image?"
    elif result["type"] == "diet":
        result["response"] += "\n🍽️ Do you want a plan for weight loss or muscle gain?"
    elif result["type"] == "pdf":
        result["response"] += "\n📄 Would you like me to search something inside the PDF?"
    elif result["type"] == "math":
        result["response"] += "\n🧮 Want help solving more equations?"

    return result
