import cv2

cap = cv2.VideoCapture(0) # Use 0 for the default webcam

while True:
    success, frame = cap.read()
    if not success:
        break

    cv2.imshow("GYM BRO Camera Test", frame)

    # Press 'q' to quit the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()