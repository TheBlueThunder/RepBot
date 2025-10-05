import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Create the pose detector object
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def detect_pose(frame):
    """
    Detects body joints in a video frame.
    
    Parameters:
    - frame: Image from camera (BGR format)
    
    Returns:
    - landmarks_dict: Dictionary with joint coordinates (or None if no person found)
    - annotated_frame: Frame with skeleton drawn on it
    """
    
    # Convert BGR to RGB (MediaPipe needs RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Run the AI model to detect pose
    results = pose.process(frame_rgb)
    
    # Make a copy of the frame to draw on
    annotated_frame = frame.copy()
    
    # Check if a person was detected
    if results.pose_landmarks:
        
        # ✨ NEW: Check if key joints are visible enough
        landmarks = results.pose_landmarks.landmark
        left_shoulder_vis = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility
        right_shoulder_vis = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility
        
        # Only proceed if at least one shoulder is clearly visible
        if left_shoulder_vis > 0.5 or right_shoulder_vis > 0.5:
            
            # Draw skeleton on the frame
            mp_drawing.draw_landmarks(
                annotated_frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=1)
            )
            
            # Get frame dimensions for converting coordinates
            height, width, _ = frame.shape
            
            # Extract the joints we need for push-ups
            landmarks_dict = {
                'left_shoulder': {
                    'x': landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * width,
                    'y': landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height,
                    'visibility': landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility
                },
                'right_shoulder': {
                    'x': landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width,
                    'y': landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height,
                    'visibility': landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility
                },
                'left_elbow': {
                    'x': landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x * width,
                    'y': landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y * height,
                    'visibility': landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].visibility
                },
                'right_elbow': {
                    'x': landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x * width,
                    'y': landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y * height,
                    'visibility': landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].visibility
                },
                'left_wrist': {
                    'x': landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x * width,
                    'y': landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y * height,
                    'visibility': landmarks[mp_pose.PoseLandmark.LEFT_WRIST].visibility
                },
                'right_wrist': {
                    'x': landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x * width,
                    'y': landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y * height,
                    'visibility': landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].visibility
                }
            }
            
            return landmarks_dict, annotated_frame
    
    # No person detected or visibility too low
    return None, annotated_frame
    
def test_pose_detection():
    """Test pose detection with camera feed"""
    
    # Connect to camera (change 0 to your DroidCam URL if needed)
    cap = cv2.VideoCapture("http://192.168.0.109:4747/video")
    
    if not cap.isOpened():
        print("ERROR: Cannot access camera")
        return
    
    print("Pose detection active!")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("ERROR: Cannot read frame")
            break
        
        # Detect pose (now returns TWO values!)
        landmarks, annotated_frame = detect_pose(frame)
        
        # Add text overlay
        if landmarks:
            cv2.putText(annotated_frame, "POSE DETECTED", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Print elbow position for debugging
            print(f"Left elbow Y: {landmarks['left_elbow']['y']:.0f} | "
                  f"Visibility: {landmarks['left_elbow']['visibility']:.2f}")
        else:
            cv2.putText(annotated_frame, "NO POSE DETECTED", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Display
        cv2.imshow("Workout Tracker - Pose Detection", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    pose.close()


if __name__ == "__main__":
    test_pose_detection()