import cv2

def start_camera_feed(camera_source=0):
    
    """
    Explanation:
    This function initializes a camera feed using OpenCV. It attempts to access the camera specified by
    the `camera_source` parameter, which can be an integer (for local webcams) or a string (for IP cameras).
    If the camera cannot be accessed, it prints an error message with troubleshooting steps.
    If the camera is successfully accessed, it continuously reads frames from the camera and displays them
    in a window called "Camera Feed". The window can be closed by pressing the 'q' key.

    Parameters:
    - camera_source: int or str, default is 0. This can be an integer for local webcams or a string for IP camera URLs.

    Returns:
    - None
    """

    cap = cv2.VideoCapture(camera_source)

    if not cap.isOpened():
        print("ERROR: Cannot access camera.")
        print("Check:")
        print("  - DroidCam app is running on your phone")
        print("  - IP address is correct")
        print("  - Phone and computer are on same WiFi")
        return  # Exit the function early
    
    print("Camera opened successfully.")
    print("Press 'q' to exit the camera feed.")

    while True:
        ret, frame = cap.read() # Capture frame-by-frame
        if not ret:
            print("ERROR: Could not read frame.")
            break

        cv2.imshow('RepBot Workout Tracker', frame)

        # Press 'q' to exit the camera feed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    while True:
        ret, frame = cap.read()
        
        # Check if frame was read successfully
        if not ret:
            print("ERROR: Cannot read frame from camera.")
            break  # Exit the loop

        # Display the frame in a window
        # "Workout Tracker - Camera Feed" is the window title
        cv2.imshow("Workout Tracker - Camera Feed", frame)

        # Wait for 1 millisecond and check if 'q' was pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting camera feed...")
            break  # Exit the loop
    
    # Cleanup - release camera and close windows
    # Always do this to free up system resources!
    cap.release()
    cv2.destroyAllWindows()
    print("Camera feed closed.")

if __name__ == "__main__":
    # For DroidCam wireless:
    # Replace with your phone's IP from DroidCam app
    droidcam_url = "http://192.168.0.109:4747/video"
    
    start_camera_feed(droidcam_url)
    
    # Once working, try with DroidCam:
    # start_camera_feed("http://YOUR_PHONE_IP:4747/video")