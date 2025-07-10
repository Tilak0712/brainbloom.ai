def solve_math(equation):
    try:
        result = eval(equation, {"__builtins__": None}, {})
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"
