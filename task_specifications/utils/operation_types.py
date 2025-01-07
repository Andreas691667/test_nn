"""This module contains the classes for the operation types used in the task specification."""

from dataclasses import dataclass


@dataclass
class Move:
    """Move class to represent a move
    :param x: x coordinate
    :type int
    :param y: y coordinate
    :type int
    :param table_distance: distance from the table in meters
    :type float
    :param rotation: rotation in radians for the end effector
    :type float
    """

    def __init__(self, x: int, y: int, table_distance: float = 0.0, rotation: float = 0.0):
        self.x = x
        self.y = y
        self.table_distance = table_distance
        self.rotation = rotation

@dataclass
class MoveGripper:
    """MoveGripper class to represent a move gripper
    :param position: relative position to move the gripper to [0;1].
    0.0 is fully open, 1.0 is fully closed
    :type float
    """

    def __init__(self, position: float = 0.0):
        self.position = position


@dataclass
class Grip:
    """Grip class to represent a grip.
    Try to grip the object
    """

    def __init__(self):
        pass
