def diet_recommendation(goal):
    goal = goal.lower()

    if "weight loss" in goal:
        return """
        💡 Weight Loss Plan:
        - 🥗 Breakfast: Oatmeal with fruits
        - 🍱 Lunch: Grilled chicken + salad
        - 🍲 Dinner: Steamed vegetables + tofu
        - 💧 Drink plenty of water
        - 🏃 30 min daily walking
        """

    elif "muscle gain" in goal:
        return """
        💪 Muscle Gain Plan:
        - 🍳 Breakfast: Eggs + whole grain toast
        - 🍚 Lunch: Brown rice + chicken breast
        - 🍝 Dinner: Pasta + beans
        - 🥤 Protein shake post-workout
        - 🏋️ Strength training 4x/week
        """

    elif "healthy lifestyle" in goal or "general fitness" in goal:
        return """
        🌱 Healthy Lifestyle Plan:
        - 🍇 Breakfast: Fresh fruit + Greek yogurt
        - 🥙 Lunch: Whole grain wrap with veggies
        - 🍲 Dinner: Lentil soup + mixed greens
        - 💧 Hydration: 2-3L water/day
        - 🚶 Walk or do light exercise daily
        """

    else:
        return """
        ⚠️ Sorry, I couldn't recognize that goal.
        Try using 'weight loss', 'muscle gain', or 'healthy lifestyle'.
        """
