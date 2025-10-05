import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QImage, QPixmap


class WorkoutOverlay(QWidget):
    """
    Fullscreen overlay window with hacker aesthetic.
    Always-on-top, semi-transparent, displays workout progress.
    Now includes camera connection screen and live feed display.
    """
    
    def __init__(self):
        """Initialize the fullscreen overlay window."""
        super().__init__()
        # Branding
        self.brand_name = "RepBot"
        self.brand_by = "Ace Technologies"
        self.exercise_name = "Push-Ups"
        
        # Window properties - fullscreen
        self.setWindowTitle(f"{self.brand_name} - {self.exercise_name}")
        
        # Make window frameless and always on top
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # Always on top
            Qt.FramelessWindowHint |   # No title bar/borders
            Qt.Tool                     # Doesn't show in taskbar
        )
        
        # Set fullscreen
        self.showFullScreen()
        
        # Set transparency
        self.setWindowOpacity(0.85)
        
        # Set background color and style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(5, 5, 10, 200);
                border: 3px solid #00ff00;
            }
        """)
        
        # Create layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(30)
        self.setLayout(self.layout)
        
        # Add vertical stretch to center content
        self.layout.addStretch()
        
        # Create CONNECTION SCREEN labels
        self.connection_header = self._create_label(
            f"╔════════════════════════════════════════════════════╗\n"
            f"║        {self.brand_name}        ║\n"
            f"║        by {self.brand_by}        ║\n"
            f"╚════════════════════════════════════════════════════╝",
            size=28, color="#00ffff"
        )
        
        self.connection_status = self._create_label(
            "> INITIALIZING CAMERA SUBSYSTEM...\n"
            "> Establishing connection to video feed...\n"
            "> Please wait...",
            size=18, color="#00ff00"
        )
        
        self.connection_animation = self._create_label(
            "[████░░░░░░] 40%",
            size=16, color="#00ff00"
        )
        
        # Create MAIN WORKOUT labels
        self.header_label = self._create_label(
            f"╔════════════════════════════════════════════════════╗\n"
            f"║        {self.brand_name}        ║\n"
            f"║        by {self.brand_by}        ║\n"
            f"╚════════════════════════════════════════════════════╝",
            size=28, color="#00ffff"
        )
        
        self.exercise_label = self._create_label(
            f"EXERCISE: {self.exercise_name}",
            size=22, color="#00ff00"
        )
        
        self.set_label = self._create_label(
            "SET STATUS : [──────────] 0/5",
            size=20, color="#00ff00"
        )
        
        self.rep_label = self._create_label(
            "REP STATUS : [──────────] 0/12",
            size=20, color="#00ff00"
        )
        
        self.message_label = self._create_label(
            "> SYSTEM: Awaiting calibration...", 
            size=16, color="#00ff00"
        )
        
        # Camera feed label (positioned in corner)
        self.camera_label = QLabel()
        self.camera_label.setStyleSheet("""
            border: 2px solid #00ff00;
            background-color: rgba(0, 0, 0, 150);
        """)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setFixedSize(320, 240)  # Fixed size for camera feed
        
        self.footer_label = self._create_label(
            "\n[Press 'q' to terminate session]", 
            size=14, color="#888888"
        )
        
        # Start with connection screen
        self._show_connection_screen()
        
        # Data tracking
        self.current_reps = 0
        self.current_sets = 0
        self.total_reps = 12
        self.total_sets = 5
        
        # Connection animation state
        self.connection_progress = 0
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._animate_connection)
        
    def _create_label(self, text, size=10, color="#00ff00"):
        """
        Create a styled label with monospace font.
        
        Parameters:
        - text: Text to display
        - size: Font size
        - color: Hex color code
        
        Returns:
        - QLabel widget
        """
        label = QLabel(text)
        font = QFont("Courier New", size)
        font.setWeight(QFont.Bold)
        label.setFont(font)
        label.setStyleSheet(f"color: {color}; background: transparent;")
        label.setAlignment(Qt.AlignCenter)
        return label
    
    def _show_connection_screen(self):
        """Display the camera connection screen."""
        # Clear layout
        self._clear_layout()
        
        # Add connection screen elements
        self.layout.addStretch()
        self.layout.addWidget(self.connection_header)
        self.layout.addSpacing(60)
        self.layout.addWidget(self.connection_status)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.connection_animation)
        self.layout.addStretch()
        
    def _show_main_screen(self):
        """Display the main workout tracking screen."""
        # Clear layout
        self._clear_layout()
        
        # Add main screen elements with camera feed
        self.layout.addWidget(self.header_label)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.exercise_label)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.set_label)
        self.layout.addWidget(self.rep_label)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.message_label)
        self.layout.addStretch()
        # Camera feed in the center
        self.layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.footer_label)
        
    def _clear_layout(self):
        """Remove all widgets from layout."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _animate_connection(self):
        """Animate the connection progress bar."""
        self.connection_progress += 10
        if self.connection_progress <= 30:
            self.connection_status.setText(
                "> INITIALIZING CAMERA SUBSYSTEM...\n"
                "> Establishing connection to video feed...\n"
                "> Please wait..."
            )
        elif self.connection_progress <= 60:
            self.connection_status.setText(
                "> CAMERA CONNECTED!\n"
                "> Calibrating pose detection...\n"
                "> Please hold push-up position."
            )
        elif self.connection_progress <= 90:
            self.connection_status.setText(
                "> CALIBRATION COMPLETE!\n"
                "> Preparing workout interface...\n"
                "> Almost ready!"
            )
        else:
            self.connection_status.setText(
                "> SYSTEM READY!\n"
                "> Starting workout...\n"
                "> Good luck!"
            )
        # Update progress bar
        filled = self.connection_progress // 10
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        self.connection_animation.setText(f"[{bar}] {self.connection_progress}%")
        # Stop when complete
        if self.connection_progress >= 100:
            self.connection_timer.stop()

    def start_connection_animation(self):
        """Start the connection animation."""
        self.connection_progress = 0
        self.connection_timer.start(200)  # Update every 200ms
    
    def switch_to_main_screen(self):
        """Switch from connection screen to main workout screen."""
        self._show_main_screen()
    
    def update_camera_feed(self, frame):
        """
        Update the camera feed display in the corner.
        
        Parameters:
        - frame: OpenCV frame (BGR format)
        """
        if frame is None:
            return
        
        # Resize frame to fit the label
        frame_resized = cv2.resize(frame, (320, 240))
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Convert to QImage
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Display in label
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))
    
    def _generate_progress_bar(self, current, total, length=10):
        """
        Generate ASCII progress bar.
        
        Parameters:
        - current: Current progress value
        - total: Total/max value
        - length: Length of bar in characters
        
        Returns:
        - String like "[███───────]"
        """
        if total == 0:
            filled = 0
        else:
            filled = int((current / total) * length)
        
        empty = length - filled
        bar = "█" * filled + "─" * empty
        return f"[{bar}]"
    
    def update_progress(self, reps, sets, total_reps, total_sets, message=None):
        """
        Update the overlay with new workout data.
        
        Parameters:
        - reps: Current reps in this set
        - sets: Current set number
        - total_reps: Reps per set
        - total_sets: Total number of sets
        - message: Optional status message
        """
        self.current_reps = reps
        self.current_sets = sets
        self.total_reps = 12  # Always show out of 12
        self.total_sets = 5   # Always show out of 5
        
        # Generate progress bars
        set_bar = self._generate_progress_bar(sets, 5, 10)
        rep_bar = self._generate_progress_bar(reps, 12, 10)
        
        # Update labels
        self.set_label.setText(f"SET STATUS : {set_bar} {sets}/5")
        self.rep_label.setText(f"REP STATUS : {rep_bar} {reps}/12")
        
        # Update message if provided
        if message:
            self.message_label.setText(message)

    def update_calibrating(self):
        self.message_label.setText("> SYSTEM: Calibrating... Hold push-up position!")

    def update_ready(self):
        self.message_label.setText("> SYSTEM: Calibration complete! Start your reps!")

    def update_complete(self):
        self.message_label.setText("> WORKOUT COMPLETE! Congratulations!")
        self.set_label.setText("SET STATUS : [██████████] DONE!")
        self.rep_label.setText("REP STATUS : [██████████] DONE!")


def test_overlay():
    """Test the overlay with simulated progress and connection screen."""
    app = QApplication(sys.argv)
    overlay = WorkoutOverlay()
    overlay.show()
    
    # Start connection animation
    overlay.start_connection_animation()
    
    # Switch to main screen after 2.5 seconds
    QTimer.singleShot(2500, overlay.switch_to_main_screen)
    
    # Simulate workout progress with timer
    counter = {'reps': 0, 'sets': 1}
    
    def simulate_rep():
        counter['reps'] += 1
        
        if counter['reps'] > 12:
            counter['reps'] = 0
            counter['sets'] += 1
            
            if counter['sets'] > 3:
                overlay.update_complete()
                timer.stop()
                return
            
            overlay.update_progress(
                counter['reps'], 
                counter['sets'], 
                12, 
                3, 
                f"ALERT: Set {counter['sets']-1} complete. Rest period initiated."
            )
        else:
            overlay.update_progress(
                counter['reps'], 
                counter['sets'], 
                12, 
                3, 
                f"INFO: Rep {counter['reps']} registered. Continue sequence."
            )
    
    # Update every 2 seconds for testing
    timer = QTimer()
    timer.timeout.connect(simulate_rep)
    
    # Show initial calibration after switching to main screen
    QTimer.singleShot(3000, lambda: overlay.update_calibrating())
    
    # After 5 seconds, show ready
    QTimer.singleShot(5000, lambda: overlay.update_ready())
    
    # After 6 seconds, start counting
    QTimer.singleShot(6000, lambda: timer.start(2000))
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_overlay()