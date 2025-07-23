import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
import os
from gtts import gTTS
from playsound import playsound
import planner 
import ollama

# --- PAGE CONFIG & INITIALIZATION ---
st.set_page_config(
    page_title="GYM BRO",
    page_icon="🦾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Explicitly define the client to connect to the default Ollama server
client = ollama.Client(host='http://127.0.0.1:11434')

# --- HELPER FUNCTIONS ---
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360 - angle if angle > 180.0 else angle

def speak(text, filename="speech.mp3"):
    try:
        if os.path.exists(filename): os.remove(filename)
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        playsound(filename, block=False)
    except Exception as e:
        print(f"Error in speak function: {e}")

def get_ai_motivation(goal, exercise, progress, set_num, total_sets):
    prompt = f"""
    The user's goal is to '{goal}'.
    They just finished set {set_num} of {total_sets}, completing {progress} of {exercise}.
    Write one short, powerful, encouraging sentence that connects this specific achievement to their main goal.
    Sound like an enthusiastic gym buddy. Don't be generic.
    """
    try:
        response = client.chat(model='gemma:2b', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        print(f"AI Motivation Error: {e}")
        return "Great work! Keep pushing."

def initialize_state():
    st.session_state.page = 'welcome'
    st.session_state.goal = ''
    st.session_state.plan = None
    st.session_state.nutrition_tip = None
    st.session_state.current_exercise_index = 0
    st.session_state.counter = 0
    st.session_state.stage = None
    st.session_state.feedback = "Let's get started!"
    st.session_state.feedback_type = "info"
    st.session_state.elapsed_time = 0.0
    st.session_state.timer_started = False
    st.session_state.last_time = 0.0
    st.session_state.user_ready = False

# Initialize state for the first run
if 'page' not in st.session_state:
    initialize_state()
    st.session_state.age = 25
    st.session_state.weight = 70.0
    st.session_state.height = 175.0
    st.session_state.steps = 0
    st.session_state.water = 0

# --- SIDEBAR FOR NAVIGATION ---
with st.sidebar:
    st.title("GYM BRO Menu")
    if st.button("💪 Start New Workout"):
        initialize_state()
        st.rerun()
    if st.button("📊 Daily Dashboard"):
        st.session_state.page = 'dashboard'
        st.rerun()

# --- ======================== UI & LOGIC ======================== ---

if st.session_state.page == 'dashboard':
    st.title("📊 Daily Habits Dashboard")
    st.write("Log your daily progress to build healthy habits!")
    st.divider()
    st.subheader("💧 Water Intake")
    water_goal = 2500
    st.session_state.water = st.number_input("Log your water intake (ml)", value=st.session_state.water, step=250, min_value=0)
    st.progress(st.session_state.water / water_goal if water_goal > 0 else 0)
    st.write(f"{st.session_state.water} / {water_goal} ml")
    st.divider()
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
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.age = st.number_input("Your Age", min_value=1, max_value=120, value=st.session_state.age, step=1)
        st.session_state.height = st.number_input("Your Height (cm)", min_value=1.0, value=st.session_state.height, step=0.1)
    with col2:
        st.session_state.weight = st.number_input("Your Weight (kg)", min_value=1.0, value=st.session_state.weight, step=0.1)
    user_goal = st.text_input("What is your main fitness goal today?", placeholder="e.g., build muscle, or lose weight")
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
    if st.session_state.nutrition_tip is None:
         with st.spinner("Analyzing your nutritional needs..."):
            st.session_state.nutrition_tip = planner.get_nutrition_advice(st.session_state.goal, st.session_state.age, st.session_state.weight, st.session_state.height)

    with st.expander("Show My AI Nutrition Tip", expanded=True):
        st.success(f"**GYM BRO says:** {st.session_state.nutrition_tip}")

    if st.session_state.plan:
        st.write(f"Here is a workout to help you **{st.session_state.goal}**:")
        for i, ex in enumerate(st.session_state.plan):
            st.write(f"**{i+1}. {ex['exercise']}**: {ex['target']} {ex['type']}")
        if st.button("Let's Go! Start Workout"):
            st.session_state.page = 'workout'
            speak(f"Starting workout. First up: {st.session_state.plan[0]['target']} {st.session_state.plan[0]['type']} of {st.session_state.plan[0]['exercise']}.")
            st.rerun()

elif st.session_state.page in ['workout', 'rest']:
    st.title("Live AI Coach")
    exercise_data = st.session_state.plan[st.session_state.current_exercise_index]
    exercise_name, exercise_type, target_value = exercise_data['exercise'], exercise_data['type'], exercise_data['target']
    
    if st.session_state.page == 'rest':
        st.balloons()
        progress_val_text = f"{st.session_state.counter} reps" if exercise_type == 'reps' else f"{target_value} seconds"
        speak("Great set! Time to rest.")
        with st.spinner("GYM BRO is thinking of some encouragement..."):
            motivation = get_ai_motivation(st.session_state.goal, exercise_name, progress_val_text, st.session_state.current_exercise_index + 1, len(st.session_state.plan))
        speak(motivation)
        st.success(motivation)
        rest_time = 15
        progress_bar = st.progress(1.0)
        st_rest_header = st.header(f"Rest: {rest_time}s")
        for i in range(rest_time, 0, -1):
            st_rest_header.header(f"Rest: {i}s")
            time.sleep(1)
            progress_bar.progress(float(i) / rest_time)
        st.session_state.current_exercise_index += 1
        if st.session_state.current_exercise_index >= len(st.session_state.plan):
            st.session_state.page = 'finished'
        else:
            st.session_state.page = 'workout'
            st.session_state.counter = 0; st.session_state.stage = None; st.session_state.elapsed_time = 0.0; st.session_state.timer_started = False; st.session_state.last_time = 0.0; st.session_state.user_ready = False
            next_ex = st.session_state.plan[st.session_state.current_exercise_index]
            speak(f"Rest over. Next up: {next_ex['target']} {next_ex['type']} of {next_ex['exercise']}.")
        st.rerun()

    # --- WORKOUT PAGE LOGIC ---
    FRAME_WINDOW = st.image([])
    col1, col2 = st.columns([1, 1])
    with col1:
        st_exercise = st.empty()
        st_target = st.empty()
        st_progress = st.empty()
    with col2:
        st_feedback_header = st.empty()
        st_feedback = st.empty()
        st_skip_button = st.empty()

    if st_skip_button.button("Skip to Rest", use_container_width=True):
        st.session_state.page = 'rest'; st.rerun()

    if exercise_type == 'time' and not st.session_state.user_ready:
        st.info("Get into position, then press Start Timer.")
        if st.button("I'm ready! Start Timer", use_container_width=True):
            st.session_state.user_ready = True
            st.rerun()
        st.stop()
    
    cap = cv2.VideoCapture(0)
    mp_pose = mp.solutions.pose
    frame_count = 0
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened() and st.session_state.page == 'workout':
            success, image = cap.read()
            if not success: break
            frame_count += 1
            if frame_count % 2 != 0: continue

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            is_complete = False
            try:
                landmarks = results.pose_landmarks.landmark
                mp_p = mp.solutions.pose.PoseLandmark
                
                # Check for visibility of key joints
                primary_joints = [mp_p.LEFT_SHOULDER, mp_p.LEFT_HIP, mp_p.LEFT_KNEE, mp_p.RIGHT_KNEE, mp_p.LEFT_ANKLE, mp_p.RIGHT_ANKLE]
                primary_joints_visible = all(landmarks[joint].visibility > 0.7 for joint in primary_joints)
                
                if not primary_joints_visible:
                    st.session_state.feedback = "I can't see you clearly! Stand further back."
                    st.session_state.feedback_type = "warning"
                else:
                    # --- Exercise Logic ---
                    if 'Squat' in exercise_name:
                        hip = [landmarks[mp_p.LEFT_HIP.value].x, landmarks[mp_p.LEFT_HIP.value].y]
                        knee = [landmarks[mp_p.LEFT_KNEE.value].x, landmarks[mp_p.LEFT_KNEE.value].y]
                        ankle = [landmarks[mp_p.LEFT_ANKLE.value].x, landmarks[mp_p.LEFT_ANKLE.value].y]
                        angle = calculate_angle(hip, knee, ankle)
                        if angle > 165: 
                            st.session_state.stage = "up"; st.session_state.feedback = "Ready to squat."; st.session_state.feedback_type = "info"
                        elif angle < 90 and st.session_state.stage == 'up':
                            st.session_state.stage = "down"; st.session_state.counter += 1; speak(str(st.session_state.counter)); st.session_state.feedback = "Good depth!"; st.session_state.feedback_type = "success"
                        elif angle > 90 and st.session_state.stage == 'up':
                            st.session_state.feedback = "Go lower!"; st.session_state.feedback_type = "warning"

                    # FIX: New logic for tracking lunges
                    elif 'Lunge' in exercise_name:
                        left_hip = [landmarks[mp_p.LEFT_HIP.value].x, landmarks[mp_p.LEFT_HIP.value].y]
                        left_knee = [landmarks[mp_p.LEFT_KNEE.value].x, landmarks[mp_p.LEFT_KNEE.value].y]
                        left_ankle = [landmarks[mp_p.LEFT_ANKLE.value].x, landmarks[mp_p.LEFT_ANKLE.value].y]
                        right_hip = [landmarks[mp_p.RIGHT_HIP.value].x, landmarks[mp_p.RIGHT_HIP.value].y]
                        right_knee = [landmarks[mp_p.RIGHT_KNEE.value].x, landmarks[mp_p.RIGHT_KNEE.value].y]
                        right_ankle = [landmarks[mp_p.RIGHT_ANKLE.value].x, landmarks[mp_p.RIGHT_ANKLE.value].y]
                        
                        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
                        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

                        if left_knee_angle > 160 and right_knee_angle > 160:
                            st.session_state.stage = "up"
                            st.session_state.feedback = "Ready to lunge."
                            st.session_state.feedback_type = "info"
                        
                        # Check if one knee is bent and the other is straight-ish
                        if (left_knee_angle < 100 or right_knee_angle < 100) and st.session_state.stage == 'up':
                            st.session_state.stage = "down"
                            st.session_state.counter += 1
                            speak(str(st.session_state.counter))
                            st.session_state.feedback = "Great lunge!"
                            st.session_state.feedback_type = "success"
                    
                    elif 'Push-up' in exercise_name:
                        shoulder = [landmarks[mp_p.LEFT_SHOULDER.value].x, landmarks[mp_p.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[mp_p.LEFT_ELBOW.value].x, landmarks[mp_p.LEFT_ELBOW.value].y]
                        wrist = [landmarks[mp_p.LEFT_WRIST.value].x, landmarks[mp_p.LEFT_WRIST.value].y]
                        angle = calculate_angle(shoulder, elbow, wrist)
                        if angle > 160: 
                            st.session_state.stage = "up"; st.session_state.feedback = "Ready."; st.session_state.feedback_type = "info"
                        if angle < 90 and st.session_state.stage == 'up':
                            st.session_state.stage = "down"; st.session_state.counter += 1; speak(str(st.session_state.counter)); st.session_state.feedback = "Great push!"; st.session_state.feedback_type = "success"
                    
                    elif 'Jumping Jack' in exercise_name:
                        l_wrist_y = landmarks[mp_p.LEFT_WRIST.value].y; l_shoulder_y = landmarks[mp_p.LEFT_SHOULDER.value].y
                        if l_wrist_y > l_shoulder_y: 
                            st.session_state.stage = "down"; st.session_state.feedback = "Jump!"; st.session_state.feedback_type = "info"
                        if l_wrist_y < l_shoulder_y and st.session_state.stage == "down":
                            st.session_state.stage = "up"; st.session_state.counter += 1; speak(str(st.session_state.counter)); st.session_state.feedback_type = "success"
                    
                    elif 'Plank' in exercise_name:
                        if st.session_state.user_ready:
                            shoulder = [landmarks[mp_p.LEFT_SHOULDER.value].x, landmarks[mp_p.LEFT_SHOULDER.value].y]
                            hip = [landmarks[mp_p.LEFT_HIP.value].x, landmarks[mp_p.LEFT_HIP.value].y]
                            ankle = [landmarks[mp_p.LEFT_ANKLE.value].x, landmarks[mp_p.LEFT_ANKLE.value].y]
                            angle = calculate_angle(shoulder, hip, ankle)
                            if angle > 155 and angle < 195:
                                if not st.session_state.timer_started:
                                    st.session_state.timer_started = True; st.session_state.last_time = time.time(); st.session_state.feedback = "Great form! Hold it."; st.session_state.feedback_type = "success"
                                else:
                                    current_time = time.time(); st.session_state.elapsed_time += current_time - st.session_state.last_time; st.session_state.last_time = current_time
                            else:
                                if st.session_state.timer_started:
                                    st.session_state.timer_started = False; st.session_state.feedback = "Straighten your back!"; st.session_state.feedback_type = "warning"
                
                if exercise_type == 'reps' and st.session_state.counter >= target_value: is_complete = True
                elif exercise_type == 'time' and st.session_state.elapsed_time >= target_value: is_complete = True
            
            except Exception as e:
                st.session_state.feedback = "Tracking... get into position."
                st.session_state.feedback_type = "info"
            
            # --- UI Updates ---
            FRAME_WINDOW.image(image, channels='BGR')
            st_exercise.subheader(f"Current Exercise: {exercise_name}")
            st_target.subheader(f"Target: {target_value} {exercise_type}")
            progress_val = st.session_state.counter if exercise_type == 'reps' else st.session_state.elapsed_time
            st_progress.header(f"Your Progress: {int(progress_val)}")
            st_feedback_header.subheader("GYM BRO Feedback:")
            if st.session_state.feedback_type == "success": st_feedback.success(st.session_state.feedback)
            elif st.session_state.feedback_type == "warning": st_feedback.warning(st.session_state.feedback)
            else: st_feedback.info(st.session_state.feedback)

            if is_complete:
                st.session_state.page = 'rest'
                cap.release()
                st.rerun()
    cap.release()

elif st.session_state.page == 'finished':
    st.title("🎉 Workout Complete! 🎉"); st.balloons()
    speak("Congratulations! You completed your workout. Well done!")
    st.success("You have successfully completed the workout plan. Great job!")
    if st.button("Do Another Workout"): 
        initialize_state()
        st.rerun()