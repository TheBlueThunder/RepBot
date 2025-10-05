import sys
import cv2
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer

from pose_detection import detect_pose
from rep_counter import RepCounter
from overlay import WorkoutOverlay


class WorkoutThread(QThread):
    """
    Separate thread for camera/pose detection.
    Prevents GUI from freezing.
    """
    
    # Signals to communicate with overlay
    update_progress = pyqtSignal(int, int, int, int, str)
    update_camera_frame = pyqtSignal(object)  # NEW: Send camera frames to overlay
    camera_connected = pyqtSignal()  # NEW: Signal when camera connects
    calibrating = pyqtSignal()
    ready = pyqtSignal()
    complete = pyqtSignal()
    
    def __init__(self, camera_source):
        super().__init__()
        self.camera_source = camera_source
        self.running = True
        self.counter = RepCounter(reps_per_set=12, total_sets=3)
    
    def run(self):
        """Main workout tracking loop."""
        max_attempts = 5
        attempt = 1
        cap = None
        
        while attempt <= max_attempts:
            cap = cv2.VideoCapture(self.camera_source)
            if cap.isOpened():
                break
                
            print(f"Camera connection attempt {attempt} of {max_attempts} failed")
            self.update_progress.emit(0, 0, 0, 0, f"CONNECTION ATTEMPT {attempt}/{max_attempts}")
            attempt += 1
            time.sleep(2)  # Wait 2 seconds between attempts
            
        if not cap or not cap.isOpened():
            print("ERROR: Cannot access camera after all attempts")
            self.update_progress.emit(0, 0, 0, 0, "CAMERA CONNECTION FAILED")
            return
            
        print("Workout tracker started!")
        time.sleep(3)  # Extra delay to ensure stable connection
        
        # Signal that camera is connected
        self.camera_connected.emit()
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect pose
            landmarks, annotated_frame = detect_pose(frame)
            
            # Send camera frame to overlay for display in corner
            self.update_camera_frame.emit(annotated_frame)
            
            # Calibration phase
            if not self.counter.is_calibrated:
                self.calibrating.emit()
                self.counter.calibrate(landmarks)
                
                if self.counter.is_calibrated:
                    self.ready.emit()
            else:
                # Counting phase
                progress = self.counter.count_rep(landmarks)
                
                # Update overlay
                message = f"STATUS: Set {progress['sets']}, Rep {progress['reps']} - Position: {progress['state']}"
                self.update_progress.emit(
                    progress['reps'],
                    progress['sets'],
                    self.counter.reps_per_set,
                    self.counter.total_sets,
                    message
                )
                
                # Check completion
                if progress['completed']:
                    self.complete.emit()
                    self.running = False
            
            # Optional: Display camera feed in separate window (for debugging)
            # cv2.imshow("Camera Feed", annotated_frame)
            
            # Check for 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    def stop(self):
        """Stop the workout thread."""
        self.running = False


def main():
    """Main function to run the complete workout tracker."""
    
    # Create PyQt application
    app = QApplication(sys.argv)
    
    # Create overlay
    overlay = WorkoutOverlay()
    
    # Start connection animation
    overlay.start_connection_animation()
    
    # Show overlay
    overlay.show()
    
    # Create workout thread
    camera_source = "http://192.168.0.109:4747/video"  # Change to your camera
    # camera_source = 0  # Or use laptop webcam
    
    workout_thread = WorkoutThread(camera_source)
    
    # Connect signals to overlay methods
    workout_thread.update_progress.connect(overlay.update_progress)
    workout_thread.update_camera_frame.connect(overlay.update_camera_feed)
    workout_thread.calibrating.connect(overlay.update_calibrating)
    workout_thread.ready.connect(overlay.update_ready)
    workout_thread.complete.connect(overlay.update_complete)
    
    # When camera connects, switch to main screen after a short delay
    def on_camera_connected():
        # Give the connection animation time to finish
        QTimer.singleShot(2000, overlay.switch_to_main_screen)
    
    workout_thread.camera_connected.connect(on_camera_connected)
    
    # Start workout tracking (starts immediately but overlay shows connection first)
    workout_thread.start()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()