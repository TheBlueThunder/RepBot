from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from exercises import ExerciseType

class ExerciseSelector(QWidget):
    """Exercise selection screen with cyberpunk aesthetic"""
    
    exercise_selected = pyqtSignal(ExerciseType)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        # Window properties
        self.setWindowTitle("RepBot - Exercise Selection")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self.setWindowOpacity(0.85)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(5, 5, 10, 200);
                border: 3px solid #00ff00;
            }
            QPushButton {
                background-color: rgba(0, 255, 0, 30);
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 15px;
                margin: 10px;
                font-family: 'Courier New';
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 0, 80);
            }
        """)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(
            "╔════════════════════════════════════════════════════╗\n"
            "║                    RepBot                          ║\n"
            "║              Exercise Selection                    ║\n"
            "╚════════════════════════════════════════════════════╝"
        )
        header.setFont(QFont("Courier New", 24))
        header.setStyleSheet("color: #00ffff; border: none;")
        header.setAlignment(Qt.AlignCenter)
        
        # Instructions
        instructions = QLabel("Select your exercise:")
        instructions.setFont(QFont("Courier New", 16))
        instructions.setStyleSheet("color: #00ff00; border: none;")
        instructions.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addSpacing(40)
        layout.addWidget(instructions)
        layout.addSpacing(20)
        
        # Add exercise buttons
        for exercise_type in ExerciseType:
            btn = QPushButton(f"[ {exercise_type.value} ]")
            btn.clicked.connect(lambda checked, ex=exercise_type: self.on_exercise_selected(ex))
            layout.addWidget(btn)
            
        # Add vertical stretch for spacing
        layout.addStretch()
        
        # Exit instruction
        exit_label = QLabel("[Press ESC to exit]")
        exit_label.setFont(QFont("Courier New", 12))
        exit_label.setStyleSheet("color: #888888; border: none;")
        exit_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(exit_label)
        
        self.setLayout(layout)
        
    def on_exercise_selected(self, exercise_type):
        """Emit signal when exercise is selected"""
        self.exercise_selected.emit(exercise_type)
        self.close()
        
    def keyPressEvent(self, event):
        """Handle escape key to exit"""
        if event.key() == Qt.Key_Escape:
            self.close()