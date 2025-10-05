# RepBot - AI-Powered Workout Tracker

RepBot is an AI-powered workout tracking system that uses computer vision to count exercise repetitions and monitor form in real-time. With its cyberpunk-inspired interface and advanced pose detection, it provides an engaging way to track your workouts.

## Features

- Real-time pose detection and exercise tracking
- Support for multiple exercises:
  - Push-ups
  - Squats
  - Sit-ups
  - Jumping Jacks
  - Lunges
- Cyberpunk-themed GUI with live camera feed
- Auto-calibration for different body types and positions
- Set and rep counting with progress visualization
- Support for DroidCam as camera source

## Requirements

- Python 3.10+
- OpenCV
- MediaPipe
- PyQt5
- DroidCam (optional, for using phone camera)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RepBot.git
cd RepBot
```

2. Create a virtual environment:
```bash
python -m venv workout_env
```

3. Activate the virtual environment:
- Windows:
  ```bash
  workout_env\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source workout_env/bin/activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Select your exercise from the menu

3. Follow the on-screen calibration instructions

4. Start your workout!

## Configuration

- Camera source can be changed in `main.py`
- Exercise parameters can be adjusted in `exercises.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## How It Works

RepBot uses MediaPipe's pose detection to track 33 key body points in real-time. The application processes these points to:
- Calculate joint angles and body positions
- Detect exercise movements using custom algorithms
- Track repetitions based on movement patterns
- Monitor form and provide feedback

### Tech Stack
- Python for core functionality
- MediaPipe for pose detection
- OpenCV for video processing
- PyQt5 for the graphical interface
- NumPy for mathematical calculations

## License

This project is licensed under the MIT License - see the LICENSE file for details.