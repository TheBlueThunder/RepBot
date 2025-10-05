from enum import Enum

class ExerciseType(Enum):
    PUSHUPS = "Push-Ups"
    SQUATS = "Squats"
    SITUPS = "Sit-Ups"
    JUMPING_JACKS = "Jumping Jacks"
    LUNGES = "Lunges"

class Exercise:
    def __init__(self, type: ExerciseType, joint_pairs: list, range_threshold: float = 0.35):
        self.type = type
        self.joint_pairs = joint_pairs  # List of joint pairs to track
        self.range_threshold = range_threshold  # Movement range threshold
        
    def get_tracking_points(self):
        """Returns the list of body points needed for this exercise"""
        points = set()
        for pair in self.joint_pairs:
            points.update(pair)
        return list(points)

# Exercise definitions with their tracking joints
EXERCISES = {
    ExerciseType.PUSHUPS: Exercise(
        ExerciseType.PUSHUPS,
        [
            ('left_shoulder', 'left_elbow'),
            ('right_shoulder', 'right_elbow')
        ]
    ),
    ExerciseType.SQUATS: Exercise(
        ExerciseType.SQUATS,
        [
            ('left_hip', 'left_knee'),
            ('right_hip', 'right_knee')
        ],
        0.4  # Larger range for squats
    ),
    ExerciseType.SITUPS: Exercise(
        ExerciseType.SITUPS,
        [
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip')
        ]
    ),
    ExerciseType.JUMPING_JACKS: Exercise(
        ExerciseType.JUMPING_JACKS,
        [
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_ankle', 'right_ankle')
        ],
        0.45  # Need wider range for jumping jacks
    ),
    ExerciseType.LUNGES: Exercise(
        ExerciseType.LUNGES,
        [
            ('left_knee', 'left_ankle'),
            ('right_knee', 'right_ankle'),
            ('left_hip', 'left_knee'),
            ('right_hip', 'right_knee')
        ],
        0.3  # More precise for lunges
    )
}

# Implementation notes for each exercise:

"""
SQUATS:
- Track hip-to-knee angle on both sides
- Down state: angle decreases (knees bend)
- Up state: angle increases (standing)
- Key points: Make sure back stays straight (could add shoulder tracking)

SITUPS:
- Track shoulder-to-hip angle
- Down state: person lying flat (angle ~180°)
- Up state: person sitting up (angle ~90°)
- Can add elbow tracking for hands-behind-head form check

JUMPING JACKS:
- Track both arm spread (shoulder width) and leg spread
- Down state: arms and legs together
- Up state: arms and legs spread
- Need to track timing/rhythm for proper form

LUNGES:
- Track hip-knee-ankle alignment
- Down state: back knee near ground
- Up state: both legs straight
- Need to alternate legs and track proper knee angles
"""