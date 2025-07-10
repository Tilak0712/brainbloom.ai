def smart_router(user_input=None, uploaded_file=None):
    try:
        if uploaded_file:
            name = uploaded_file.name.lower()

            # ✅ 1. PDF Files
            if name.endswith('.pdf'):
                result = extract_text_from_pdf(uploaded_file)
                if result['mode'] == 'error':
                    return result['text']
                return f"📄 Extracted Text:\n\n{result['text'][:1500]}..."

            # ✅ 2. Image Files
            elif name.endswith(('.jpg', '.jpeg', '.png')):
                return "🖼️ Image received. (Captioning/Image Q&A coming soon)"

            # ✅ 3. Text or Python Files (pass real question)
            elif name.endswith(('.txt', '.py')):
                question = user_input or "Summarize this file."
                return handle_uploaded_file(uploaded_file, question)

            # ✅ 4. Unsupported files
            else:
                return "❌ Unsupported file type."

        if user_input:
            q = user_input.lower()

            # ✅ 5. Diet Tool
            if any(x in q for x in ["calorie", "diet", "eat", "meal", "plan"]):
                return diet_recommendation(user_input)

            # ✅ 6. Math Solver
            if any(x in q for x in ["solve", "+", "-", "*", "/", "equation", "math", "x ="]):
                return solve_math(user_input)

            # ✅ 7. Code Generator
            if any(x in q for x in ["generate code", "write a function", "python", "program"]):
                return generate_code(user_input)

            # ✅ 8. Voice Transcription
            if "transcribe audio" in q or "convert voice" in q:
                return transcribe_audio()

            # ✅ 9. Default Chatbot (with memory & smart fallback)
            return get_chat_response([{"role": "user", "content": user_input}])[0]

        return "❌ No input detected."

    except Exception as e:
        return f"❌ Error in smart_router: {e}"
