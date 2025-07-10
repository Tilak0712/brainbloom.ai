from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def generate_code(task):
    prompt = f"Write Python code for the following task:\n\n{task}\n\nCode:"
    try:
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b-instruct",  # ✅ Use one model at a time
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error generating code: {str(e)}"
