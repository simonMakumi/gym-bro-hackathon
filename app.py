import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
import os
from gtts import gTTS
from playsound import playsound
import planner # Our other python file
import ollama

# --- INITIALIZE MEDIAPIPE ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# --- HELPER FUNCTIONS ---
def calculate_angle(a, b, c):
    """Calculates the angle between three points."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360 - angle if angle > 180.0 else angle

def speak(text, filename="speech.mp3"):
    """Generates and plays an audio file from text."""
    try:
        if os.path.exists(filename): os.remove(filename)
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        playsound(filename, block=False)
    except Exception as e:
        print(f"Error in speak function: {e}")

def get_ai_motivation(goal, exercise):
    """Gets personalized motivation from Gemma."""
    prompt = f"The user's goal is to '{goal}'. They just finished a set of {exercise}. Write one short, powerful, encouraging sentence that connects the exercise to their goal."
    try:
        response = ollama.chat(model='gemma:2b', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        print(f"AI Motivation Error: {e}")
        return "Great work! Keep pushing."

# --- PAGE CONFIG & INITIALIZATION ---
st.set_page_config(page_title="GYM BRO", page_icon="🦾", layout="wide")

def initialize_state():
    """Initializes or resets the session state for a new workout."""
    # We don't reset everything, just the workout-specific parts
    st.session_state.page = 'welcome'
    st.session_state.goal = ''
    st.session_state.plan = None
    st.session_state.current_exercise_index = 0
    st.session_state.counter = 0 
    st.session_state.stage = None
    st.session_state.start_time = 0
    st.session_state.feedback = "Let's get started!"

# Initialize state for the first run
if 'page' not in st.session_state:
    initialize_state()
    # Also initialize dashboard stats for the very first run
    st.session_state.age = 25 # Default age
    st.session_state.weight = 70.0 # Default weight
    st.session_state.height = 175.0 # Default height
    st.session_state.steps = 0
    st.session_state.water = 0

# --- SIDEBAR FOR NAVIGATION ---
with st.sidebar:
    st.title("GYM BRO Menu")
    if st.button("💪 Start New Workout"):
        initialize_state() # Reset for a new workout
        st.rerun()
    if st.button("📊 Daily Dashboard"):
        st.session_state.page = 'dashboard'
        st.rerun()


# --- ======================== UI & LOGIC ======================== ---

if st.session_state.page == 'dashboard':
    st.title("📊 Daily Habits Dashboard")
    st.write("Log your daily progress to build healthy habits!")

    st.divider()

    # Water Intake Tracker
    st.subheader("💧 Water Intake")
    water_goal = 2500 # ml
    st.session_state.water = st.number_input("Log your water intake (ml)", value=st.session_state.water, step=250, min_value=0)
    st.progress(st.session_state.water / water_goal if water_goal > 0 else 0)
    st.write(f"{st.session_state.water} / {water_goal} ml")

    st.divider()

    # Step Counter
    st.subheader("👟 Daily Steps")
    step_goal = 10000
    st.session_state.steps = st.number_input("Log your steps for the day", value=st.session_state.steps, step=100, min_value=0)
    st.progress(st.session_state.steps / step_goal if step_goal > 0 else 0)
    st.write(f"{st.session_state.steps} / {step_goal} steps")
    
    st.divider()
    
    st.info("Reminder: Try to stand up and stretch for a few minutes every hour!")

elif st.session_state.page == 'welcome':
    st.title("Welcome to GYM BRO 🦾")
    st.subheader("Your Private, On-Device AI Personal Trainer")

    st.write("First, tell me a little about yourself:")
    
    # Create columns for a cleaner layout
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.age = st.number_input("Your Age", min_value=1, max_value=120, value=st.session_state.age, step=1)
        st.session_state.height = st.number_input("Your Height (cm)", min_value=1.0, value=st.session_state.height, step=0.1)
    with col2:
        st.session_state.weight = st.number_input("Your Weight (kg)", min_value=1.0, value=st.session_state.weight, step=0.1)
        
    user_goal = st.text_input("What is your main fitness goal today?", placeholder="e.g., build full body strength")

    if st.button("Generate My Workout"):
        if user_goal and st.session_state.age > 0 and st.session_state.weight > 0 and st.session_state.height > 0:
            st.session_state.goal = user_goal
            st.session_state.page = 'plan'
            st.rerun()
        else:
            st.warning("Please fill in all your details and a fitness goal.")

elif st.session_state.page == 'plan':
    st.title("Your AI-Generated Plan")
    if st.session_state.plan is None:
        with st.spinner("GYM BRO is creating your personalized plan..."):
            st.session_state.plan = planner.get_workout_plan(st.session_state.goal)

    # --- Display Nutrition Advice ---
    with st.expander("Show My AI Nutrition Tip"):
        with st.spinner("Analyzing your nutritional needs..."):
            nutrition_tip = planner.get_nutrition_advice(
                st.session_state.goal,
                st.session_state.age,
                st.session_state.weight,
                st.session_state.height
            )
            st.info(f"**GYM BRO says:** {nutrition_tip}")

    if st.session_state.plan:
        st.write(f"Here is a workout to help you **{st.session_state.goal}**:")
        for i, ex in enumerate(st.session_state.plan):
            st.write(f"**{i+1}. {ex['exercise']}**: {ex['target']} {ex['type']}")
        
        if st.button("Let's Go! Start Workout"):
            st.session_state.page = 'workout'
            speak(f"Starting workout. First up: {st.session_state.plan[0]['target']} {st.session_state.plan[0]['exercise']}.")
            st.rerun()

elif st.session_state.page in ['workout', 'rest']:
    # --- GET CURRENT EXERCISE DETAILS ---
    exercise_data = st.session_state.plan[st.session_state.current_exercise_index]
    exercise_name, exercise_type, target_value = exercise_data['exercise'], exercise_data['type'], exercise_data['target']

    st.title("Live AI Coach")
    col1, col2 = st.columns([3, 2])
    with col1: FRAME_WINDOW = st.image([])
    with col2:
        st.subheader("Current Exercise:"); st.header(f"{exercise_name}")
        st.subheader("Target:"); st.header(f"{target_value} {exercise_type}")
        progress_val = st.session_state.counter if exercise_type == 'reps' else int(time.time() - st.session_state.start_time) if st.session_state.start_time > 0 else 0
        st.subheader("Your Progress:"); st.header(f"{progress_val}")
        st.subheader("GYM BRO Feedback:"); st.info(st.session_state.feedback)

    # --- REST PAGE LOGIC ---
    if st.session_state.page == 'rest':
        st.balloons()
        with st.spinner("Getting your personalized motivation..."):
            motivation = get_ai_motivation(st.session_state.goal, exercise_name)
        speak(motivation)
        st.success(motivation)
        
        rest_time = 15
        progress_bar = st.progress(1.0)
        st_rest_header = st.header(f"Rest: {rest_time}s")
        for i in range(rest_time, 0, -1):
            st_rest_header.header(f"Rest: {i}s"); time.sleep(1); progress_bar.progress(float(i) / rest_time)
        
        st.session_state.current_exercise_index += 1
        if st.session_state.current_exercise_index >= len(st.session_state.plan):
            st.session_state.page = 'finished'
        else:
            st.session_state.page = 'workout'
            st.session_state.counter = 0; st.session_state.stage = None; st.session_state.start_time = 0
            next_ex = st.session_state.plan[st.session_state.current_exercise_index]
            speak(f"Rest over. Next up: {next_ex['target']} {next_ex['exercise']}.")
        st.rerun()

    # --- WORKOUT PAGE LOGIC ---
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened() and st.session_state.page == 'workout':
            success, image = cap.read();
            if not success: break
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB) # Flip for selfie view
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                mp_p = mp.solutions.pose.PoseLandmark
                
                # --- VISIBILITY CHECK ---
                primary_joints_visible = all(landmarks[joint].visibility > 0.6 for joint in [mp_p.LEFT_SHOULDER, mp_p.LEFT_HIP, mp_p.LEFT_KNEE])
                
                if not primary_joints_visible:
                    st.session_state.feedback = "Stand back - I can't see you clearly!"
                else:
                    # --- EXERCISE LOGIC DISPATCHER ---
                    if 'Squat' in exercise_name:
                        hip = [landmarks[mp_p.LEFT_HIP.value].x, landmarks[mp_p.LEFT_HIP.value].y]
                        knee = [landmarks[mp_p.LEFT_KNEE.value].x, landmarks[mp_p.LEFT_KNEE.value].y]
                        ankle = [landmarks[mp_p.LEFT_ANKLE.value].x, landmarks[mp_p.LEFT_ANKLE.value].y]
                        angle = calculate_angle(hip, knee, ankle)
                        
                        if angle > 165: 
                            st.session_state.stage = "up"
                            st.session_state.feedback = "Ready to squat."
                        elif angle < 90 and st.session_state.stage == 'up':
                            st.session_state.stage = "down"; st.session_state.counter += 1; speak(str(st.session_state.counter))
                            st.session_state.feedback = "Good depth!"
                        elif angle > 90 and st.session_state.stage == 'up':
                            st.session_state.feedback = "Go lower!"

                    elif 'Push-up' in exercise_name:
                        shoulder = [landmarks[mp_p.LEFT_SHOULDER.value].x, landmarks[mp_p.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[mp_p.LEFT_ELBOW.value].x, landmarks[mp_p.LEFT_ELBOW.value].y]
                        wrist = [landmarks[mp_p.LEFT_WRIST.value].x, landmarks[mp_p.LEFT_WRIST.value].y]
                        angle = calculate_angle(shoulder, elbow, wrist)
                        if angle > 160: st.session_state.stage = "up"; st.session_state.feedback = "Ready."
                        if angle < 90 and st.session_state.stage == 'up':
                            st.session_state.stage = "down"; st.session_state.counter += 1; speak(str(st.session_state.counter)); st.session_state.feedback = "Great push!"

                    elif 'Jumping Jack' in exercise_name:
                        l_wrist_y = landmarks[mp_p.LEFT_WRIST.value].y; l_shoulder_y = landmarks[mp_p.LEFT_SHOULDER.value].y
                        if l_wrist_y > l_shoulder_y: st.session_state.stage = "down"; st.session_state.feedback = "Jump!"
                        if l_wrist_y < l_shoulder_y and st.session_state.stage == "down":
                            st.session_state.stage = "up"; st.session_state.counter += 1; speak(str(st.session_state.counter))

                    elif 'Plank' in exercise_name:
                        shoulder = [landmarks[mp_p.LEFT_SHOULDER.value].x, landmarks[mp_p.LEFT_SHOULDER.value].y]
                        hip = [landmarks[mp_p.LEFT_HIP.value].x, landmarks[mp_p.LEFT_HIP.value].y]
                        ankle = [landmarks[mp_p.LEFT_ANKLE.value].x, landmarks[mp_p.LEFT_ANKLE.value].y]
                        angle = calculate_angle(shoulder, hip, ankle)
                        if angle > 155 and angle < 195:
                            if st.session_state.start_time == 0: st.session_state.start_time = time.time()
                            st.session_state.feedback = "Great form! Hold it."
                        else:
                            st.session_state.start_time = 0
                            st.session_state.feedback = "Straighten your back!"

            except Exception as e:
                # This will gracefully handle frames where landmarks aren't detected
                # print(f"Error during pose processing: {e}")
                st.session_state.feedback = "Getting ready..."

            # --- CHECK COMPLETION ---
            is_complete = False
            if exercise_type == 'reps' and st.session_state.counter >= target_value: is_complete = True
            elif exercise_type == 'time' and st.session_state.start_time > 0 and time.time() - st.session_state.start_time >= target_value: is_complete = True
            
            if is_complete:
                st.session_state.page = 'rest'
                cap.release()
                st.rerun()
            
            if results.pose_landmarks: mp_drawing.draw_landmarks(image, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
            FRAME_WINDOW.image(image, channels='BGR')
    cap.release()

elif st.session_state.page == 'finished':
    st.title("🎉 Workout Complete! 🎉"); st.balloons()
    speak("Congratulations! You completed your workout. Well done!")
    st.success("You have successfully completed the workout plan. Great job!")
    if st.button("Do Another Workout"): 
        initialize_state()
        st.rerun()