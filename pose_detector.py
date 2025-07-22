import cv2
import mediapipe as mp
import numpy as np

# Helper function to calculate angle
def calculate_angle(a, b, c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

# Initialize MediaPipe tools
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Start webcam capture
cap = cv2.VideoCapture(0)

# Setup variables for rep counting
counter = 0 
stage = None # Can be 'up' or 'down'

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Convert the BGR image to RGB before processing.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)
    
        # Convert the image back to BGR.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Check if the required landmarks are clearly visible
            hip_visibility = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
            knee_visibility = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
            ankle_visibility = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility

            if hip_visibility > 0.5 and knee_visibility > 0.5 and ankle_visibility > 0.5:
                # Get coordinates
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                
                # Calculate angle
                angle = calculate_angle(hip, knee, ankle)
                
                # Rep counting logic
                if angle > 160:
                    stage = "up"
                if angle < 90 and stage =='up':
                    stage = "down"
                    counter += 1
                    print(f"Rep Count: {counter}")
                       
        except:
            pass # Do nothing if landmarks are not detected
        
        # Display Rep Count
        # --- FIX WAS HERE ---
        cv2.putText(image, 'REPS', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
        # Draw the pose annotation on the image
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)                        

        # Display the resulting frame
        cv2.imshow('GYM BRO - Rep Counter', image)

        # Exit by pressing 'q'
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()