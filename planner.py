import ollama
import json
import re

def get_workout_plan(goal: str) -> list:
    """
    Generates a goal-specific, structured workout plan using Gemma.
    Selects from a known list of trackable exercises.
    """
    # Define the exercises our app knows how to track
    known_exercises = "'Bodyweight Squats', 'Push-ups', 'Plank', 'Jumping Jacks'"

    prompt = f"""
    You are GYM BRO, a world-class AI fitness coach. A user's goal is '{goal}'.
    Your task is to create a 3-exercise beginner bodyweight workout routine tailored to this goal.

    You MUST select exercises ONLY from this list: {known_exercises}.

    - If the goal is about 'muscle', 'strength', or 'build', focus on 'Bodyweight Squats' and 'Push-ups'.
    - If the goal is about 'lose weight', 'cardio', or 'endurance', focus on 'Jumping Jacks' and 'Plank'.
    - If the goal is about 'general fitness' or 'energy', create a balanced mix.

    IMPORTANT: Respond with ONLY a valid JSON object, and nothing else.
    The JSON must be a list of objects, each with three keys: "exercise", "type" ("reps" or "time"), and "target" (an integer).

    Example for a 'build muscle' goal:
    [
        {{"exercise": "Bodyweight Squats", "type": "reps", "target": 12}},
        {{"exercise": "Push-ups", "type": "reps", "target": 10}},
        {{"exercise": "Plank", "type": "time", "target": 30}}
    ]
    """

    try:
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        content = response['message']['content']
        
        # Find and parse the JSON part of the response
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            json_string = match.group(0)
            workout_plan = json.loads(json_string)
            # Validate that the plan is not empty
            if workout_plan:
                return workout_plan
        
        # If parsing fails or plan is empty, raise error to trigger fallback
        raise ValueError("Failed to generate a valid plan from AI.")

    except Exception as e:
        print(f"An error occurred in planner, using fallback. Error: {e}")
        # Return a reliable fallback plan if the AI fails
        return [
            {"exercise": "Bodyweight Squats", "type": "reps", "target": 10},
            {"exercise": "Jumping Jacks", "type": "reps", "target": 20},
            {"exercise": "Plank", "type": "time", "target": 30}
        ]

def get_nutrition_advice(goal: str, age: int, weight: float, height: float) -> str:
    """
    Generates simple, goal-oriented nutrition advice using Gemma.
    """
    prompt = f"""
    You are GYM BRO, an expert AI fitness coach.
    A user's stats are: Age({age}), Weight({weight}kg), Height({height}cm).
    Their primary goal is '{goal}'.

    Based on this, provide a simple, one-paragraph nutritional tip. Do not prescribe a detailed meal plan.
    - If the goal is 'build muscle', suggest high-protein foods.
    - If the goal is 'lose weight', suggest a slight calorie deficit and eating whole foods.
    - If the goal is 'general fitness', suggest a balanced diet.

    Make the advice encouraging, easy to understand, and focused on food types.
    """
    try:
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        print(f"An error occurred in the nutrition planner: {e}")
        return "Focus on a balanced diet rich in lean proteins, vegetables, and whole grains. Staying hydrated is also key!"


if __name__ == "__main__":
    print("GYM BRO AI Planner is thinking...")
    # Test with a specific goal
    user_goal = "build muscle and get stronger"
    plan = get_workout_plan(user_goal)
    print("\nGenerated Plan:")
    print(plan)