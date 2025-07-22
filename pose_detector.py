import cv2
import mediapipe as mp

# Initialize MediaPipe tools
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Start webcam capture
cap = cv2.VideoCapture(0)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # To improve performance, mark the image as not writeable.
        image.flags.writeable = False  # <-- CHANGE IS HERE
        # Convert the BGR image to RGB before processing.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Make detection
        results = pose.process(image)

        # Convert the image back to BGR and make it writeable.
        image.flags.writeable = True   # <-- AND CHANGE IS HERE
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw the pose annotation on the image.
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS)

        # Display the resulting frame
        cv2.imshow('GYM BRO - AI Pose Detector', image)

        # Exit by pressing 'q'
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()