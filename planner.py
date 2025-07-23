import ollama
import json
import re

# Explicitly define the client to connect to the default Ollama server
client = ollama.Client(host='http://127.0.0.1:11434')

def get_workout_plan(goal: str) -> list:
    """
    Generates a goal-specific, structured workout plan using Gemma.
    Selects from a known list of trackable exercises.
    """
    # FIX: Added 'Lunges' to the list of known exercises
    known_exercises = "'Bodyweight Squats', 'Push-ups', 'Plank', 'Jumping Jacks', 'Lunges'"
    
    prompt = f"""
    You are GYM BRO, a world-class AI fitness coach. A user's goal is '{goal}'.
    Your task is to create a 3-exercise beginner bodyweight workout routine tailored to this goal.

    You MUST select exercises ONLY from this list: {known_exercises}.

    - If the goal is about 'muscle', 'strength', or 'build', focus on 'Bodyweight Squats', 'Push-ups', and 'Lunges'.
    - If the goal is about 'lose weight', 'cardio', or 'endurance', focus on 'Jumping Jacks' and 'Plank'.
    - If the goal is about 'general fitness' or 'energy', create a balanced mix.
    - 'Lunges' are a great addition for any leg-focused or general fitness day.

    IMPORTANT: Respond with ONLY a valid JSON object, and nothing else.
    The JSON must be a list of objects, each with three keys: "exercise", "type" ("reps" or "time"), and "target" (an integer).
    """
    try:
        response = client.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        content = response['message']['content']
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            json_string = match.group(0)
            workout_plan = json.loads(json_string)
            if workout_plan:
                return workout_plan
        raise ValueError("Failed to generate a valid plan from AI.")
    except Exception as e:
        print(f"An error occurred in planner, using fallback. Error: {e}")
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
        response = client.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        print(f"An error occurred in the nutrition planner: {e}")
        return "Focus on a balanced diet rich in lean proteins, vegetables, and whole grains. Staying hydrated is also key!"