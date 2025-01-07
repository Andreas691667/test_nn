from task_specifications.utils.operation_types import Move, Grip, MoveGripper


def move_and_grip(x: int, y: int, rotation: float = 0.0):
    """Move to the specified x, y position and grip"""
    return [
        Move(x, y, 0.05, rotation),
        Move(x, y, 0, rotation),
        Grip(),
        Move(x, y, 0.05, rotation),
    ]


def move_and_release(x: int, y: int, rotation: float = 0.0):
    """Move to the specified x, y position and release"""
    return [
        Move(x, y, 0.05, rotation),
        Move(x, y, 0, rotation),
        MoveGripper(1.0),
        Move(x, y, 0.05, rotation),
    ]
