import cv2

class RepCounter:
    """
    Tracks push-up reps and sets based on elbow position.
    """

    THRESHOLD_BUFFER = 0.35  # Adjusted for better accuracy
    SMOOTHING_FRAMES = 5     # NEW: Require consistent position for X frames
    
    def __init__(self, reps_per_set=12, total_sets=3):
        """
        Initialize the rep counter.
        
        Parameters:
        - reps_per_set: How many reps per set (default: 12)
        - total_sets: How many sets total (default: 3)
        """

        # Configuration
        self.reps_per_set = reps_per_set
        self.total_sets = total_sets
        
        # Current progress
        self.current_rep = 0
        self.current_set = 1
        
        # State tracking
        self.position_state = "up"  # Can be "up" or "down"
        
        # NEW: Smoothing to prevent false triggers
        self.down_counter = 0  # How many frames in "down" position
        self.up_counter = 0    # How many frames in "up" position
        
        # Thresholds (we'll calibrate these)
        self.down_threshold = None  # Y value for "down" position
        self.up_threshold = None    # Y value for "up" position
        
        # Calibration data
        self.calibration_frames = []
        self.is_calibrated = False

    def calibrate(self, landmarks):
        """
        Calibrate the up and down thresholds based on initial frames.
        
        Parameters:
        - landmarks: Dictionary with joint coordinates
        
        Returns:
        - True if calibration complete, False if still calibrating
        """
        if landmarks is None:
            return False

        # Print instruction on first frame
        if len(self.calibration_frames) == 0:
            print("=" * 50)
            print("CALIBRATION MODE")
            print("=" * 50)
            print("Do 3 SLOW push-ups (take 5-6 seconds total)")
            print("Go ALL THE WAY down and ALL THE WAY up")
            print("=" * 50)

        # Choose shoulder with better visibility (MORE STABLE than elbow!)
        left_vis = landmarks['left_shoulder']['visibility']
        right_vis = landmarks['right_shoulder']['visibility']

        if left_vis > right_vis:
            joint_y = landmarks['left_shoulder']['y']
        else:
            joint_y = landmarks['right_shoulder']['y']

        # Store sample
        self.calibration_frames.append(joint_y)

        # Show progress
        progress = len(self.calibration_frames)
        if progress % 30 == 0:  # Every second
            print(f"Calibration progress: {progress}/150 frames")

        # Need MORE frames for better calibration
        if len(self.calibration_frames) < 150:  # 5 seconds instead of 3
            return False  # Still calibrating
        
        # Calculate thresholds with buffer zones
        max_y = max(self.calibration_frames)
        min_y = min(self.calibration_frames)
        range_y = max_y - min_y

        # Make sure we have enough range
        if range_y < 30:  # Less than 30 pixels of movement
            print("\n⚠️  WARNING: Not enough movement detected!")
            print("Try doing fuller push-ups during calibration")
            self.calibration_frames = []  # Reset and try again
            return False

        self.up_threshold = min_y + (range_y * self.THRESHOLD_BUFFER)
        self.down_threshold = max_y - (range_y * self.THRESHOLD_BUFFER)

        # Mark as calibrated
        self.is_calibrated = True
        self.position_state = "up"

        print("\n" + "=" * 50)
        print("✅ CALIBRATION COMPLETE!")
        print("=" * 50)
        print(f"  Up threshold: {self.up_threshold:.0f}")
        print(f"  Down threshold: {self.down_threshold:.0f}")
        print(f"  Range: {range_y:.0f} pixels")
        print("=" * 50)
        print("Starting workout tracking...\n")

        return True  # Calibration complete
    
    def count_rep(self, landmarks):
        """
        Count a rep based on shoulder position with smoothing.
        
        Parameters:
        - landmarks: Dictionary with joint coordinates
        
        Returns:
        - Dictionary with current progress
        """
        
        # Can't count if not calibrated or no person detected
        if not self.is_calibrated or landmarks is None:
            return {
                'reps': self.current_rep,
                'sets': self.current_set,
                'completed': False,
                'state': self.position_state
            }
        
        # Choose shoulder with better visibility
        left_vis = landmarks['left_shoulder']['visibility']
        right_vis = landmarks['right_shoulder']['visibility']
        
        if left_vis > right_vis:
            joint_y = landmarks['left_shoulder']['y']
            joint_name = "left shoulder"
        else:
            joint_y = landmarks['right_shoulder']['y']
            joint_name = "right shoulder"
        
        # STATE MACHINE WITH SMOOTHING
        
        if self.position_state == "up":
            # Check if shoulder went DOWN
            if joint_y > self.down_threshold:
                self.down_counter += 1
                self.up_counter = 0
                
                if self.down_counter >= self.SMOOTHING_FRAMES:
                    self.position_state = "down"
                    self.down_counter = 0
                    print(f"  ⬇ DOWN position locked ({joint_name}: {joint_y:.0f})")
            else:
                self.down_counter = 0
        
        elif self.position_state == "down":
            # Check if shoulder came back UP
            if joint_y < self.up_threshold:
                self.up_counter += 1
                self.down_counter = 0
                
                if self.up_counter >= self.SMOOTHING_FRAMES:
                    self.position_state = "up"
                    self.up_counter = 0
                    
                    # INCREMENT THE REP!
                    self.current_rep += 1
                    print(f"  ✅ REP {self.current_rep} COUNTED! ({joint_name}: {joint_y:.0f})")
                    
                    # Check if set is complete
                    if self.current_rep >= self.reps_per_set:
                        self.current_set += 1
                        self.current_rep = 0
                        print(f"\n🎯 SET {self.current_set - 1} COMPLETE!")
                        
                        # Check if all sets are done
                        if self.current_set > self.total_sets:
                            print("\n" + "🏆" * 20)
                            print("WORKOUT COMPLETE! All sets finished!")
                            print("🏆" * 20 + "\n")
                            return {
                                'reps': self.reps_per_set,
                                'sets': self.total_sets,
                                'completed': True,
                                'state': self.position_state
                            }
                        else:
                            print(f"Rest briefly, then start SET {self.current_set}...\n")
                            # ✅ FIXED: Always return after set completion
            else:
                self.up_counter = 0
        
        # ✅ ALWAYS return current progress (this line must ALWAYS be reached)
        return {
            'reps': self.current_rep,
            'sets': self.current_set,
            'completed': False,
            'state': self.position_state
        }
        
def test_rep_counter():
    """Test the complete rep counter with live camera"""
    from pose_detection import detect_pose
    
    # Connect to camera
    cap = cv2.VideoCapture("http://192.168.0.109:4747/video")
    
    if not cap.isOpened():
        print("ERROR: Cannot access camera")
        return
    
    # Create rep counter (3 sets of 5 reps for testing)
    counter = RepCounter(reps_per_set=5, total_sets=3)
        
    print("RepCounter Test Starting!")
    print("Press 'q' to quit\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect pose
        landmarks, annotated_frame = detect_pose(frame)
        
        # Calibration phase
        if not counter.is_calibrated:
            counter.calibrate(landmarks)
            cv2.putText(annotated_frame, "CALIBRATING... Do 2 slow push-ups", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            # Counting phase
            progress = counter.count_rep(landmarks)
            
            # Display progress on screen
            text = f"SET {progress['sets']}/{counter.total_sets} | REP {progress['reps']}/{counter.reps_per_set}"
            cv2.putText(annotated_frame, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Check if complete
            if progress['completed']:
                cv2.putText(annotated_frame, "WORKOUT COMPLETE!", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        
        # Display
        cv2.imshow("RepCounter Test", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_rep_counter()