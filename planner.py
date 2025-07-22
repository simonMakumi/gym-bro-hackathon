import ollama
import ast

def get_workout_plan(goal: str) -> list:
    """
    Generates a workout plan using Gemma based on a user's goal.

    Args:
        goal: The user's fitness goal (e.g., "build muscle").

    Returns:
        A list of strings, where each string is an exercise.
        Returns an empty list if an error occurs.
    """
    prompt = f"""
    You are GYM BRO, a world-class AI fitness coach. A user's goal is '{goal}'.
    Create a simple 3-exercise beginner bodyweight workout routine.

    IMPORTANT: Respond with ONLY the Python list of strings, and nothing else.
    For example: ['15 Squats', '10 Push-ups', '30 second Plank']
    """

    try:
        response = ollama.chat(
            model='gemma:2b',
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        
        # The response content should be a string that looks like a list
        plan_string = response['message']['content']
        
        # Safely evaluate the string to turn it into a real list
        workout_plan = ast.literal_eval(plan_string)
        return workout_plan

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# This block of code will only run when you execute planner.py directly
if __name__ == "__main__":
    print("GYM BRO AI Planner is thinking...")
    
    # Let's test it with a sample goal
    user_goal = "lose weight and improve cardio"
    
    plan = get_workout_plan(user_goal)
    
    if plan:
        print("\nHere is your AI-generated workout plan:")
        for i, exercise in enumerate(plan):
            print(f"  {i+1}. {exercise}")
    else:
        print("\nSorry, I couldn't generate a plan right now. Please try again.")