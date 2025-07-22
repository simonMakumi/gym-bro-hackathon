import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import planner # Our other python file

# --- HELPER FUNCTION FROM POSE_DETECTOR.PY ---
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# --- INITIALIZE MEDIAPIPE ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="GYM BRO", page_icon="🦾")

# --- SESSION STATE MANAGEMENT ---
# This is like the app's memory
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'goal' not in st.session_state:
    st.session_state.goal = ''
if 'plan' not in st.session_state:
    st.session_state.plan = None
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'stage' not in st.session_state:
    st.session_state.stage = None


# --- PAGE 1: WELCOME SCREEN ---
if st.session_state.page == 'welcome':
    st.title("Welcome to GYM BRO 🦾")
    st.write("Your on-device AI personal trainer.")
    
    user_goal = st.text_input("What is your main fitness goal today?", placeholder="e.g., lose weight, build muscle")
    
    if st.button("Generate My Plan"):
        if user_goal:
            st.session_state.goal = user_goal
            st.session_state.page = 'plan'
            st.rerun() # Rerun the script to navigate to the new page
        else:
            st.warning("Please enter a fitness goal.")

# --- PAGE 2: PLAN SCREEN ---
elif st.session_state.page == 'plan':
    st.title("Your AI-Generated Plan")
    
    if st.session_state.plan is None:
        with st.spinner("GYM BRO is creating your plan..."):
            plan_list = planner.get_workout_plan(st.session_state.goal)
            if plan_list:
                st.session_state.plan = plan_list
            else:
                st.error("Could not generate a plan. Please go back and try again.")
                if st.button("Go Back"):
                    st.session_state.page = 'welcome'
                    st.rerun()

    if st.session_state.plan:
        st.write(f"Here is a plan to help you **{st.session_state.goal}**:")
        for i, exercise in enumerate(st.session_state.plan):
            st.write(f"**{i+1}.** {exercise}")
        
        if st.button("Let's Go! Start Workout"):
            st.session_state.page = 'workout'
            st.rerun()

# --- PAGE 3: WORKOUT SCREEN ---
elif st.session_state.page == 'workout':
    st.title("Live Workout Coach")
    st.write("Let's do some squats!")

    FRAME_WINDOW = st.image([])
    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                hip_visibility = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
                knee_visibility = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
                ankle_visibility = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility

                if hip_visibility > 0.5 and knee_visibility > 0.5 and ankle_visibility > 0.5:
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                    
                    angle = calculate_angle(hip, knee, ankle)
                    
                    if angle > 160:
                        st.session_state.stage = "up"
                    if angle < 90 and st.session_state.stage =='up':
                        st.session_state.stage = "down"
                        st.session_state.counter += 1
            except:
                pass

            cv2.putText(image, 'REPS', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, str(st.session_state.counter), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)                        
            
            # This line updates the video feed in the Streamlit app
            FRAME_WINDOW.image(image, channels='BGR')

    st.success(f"Workout Complete! You did {st.session_state.counter} reps!")
    if st.button("Start Over"):
        # Reset all session state variables
        st.session_state.page = 'welcome'
        st.session_state.goal = ''
        st.session_state.plan = None
        st.session_state.counter = 0
        st.session_state.stage = None
        st.rerun()