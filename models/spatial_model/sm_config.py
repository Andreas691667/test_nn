from dataclasses import dataclass
import numpy as np

@dataclass
class Rectangle:
    """Rectangle class to represent a rectangle"""
    xmin: int = 0
    xmax: int = 0
    ymin: int = 0
    ymax: int = 0

@dataclass
class Triangle:
    """Triangle class to represent a triangle with vertices v1, v2, v3"""
    v1: tuple[int, int] = (0, 0)
    v2: tuple[int, int] = (0, 0)
    v3: tuple[int, int] = (0, 0)


# delta_h
HOLE_DIST = 0.04

# origin positions in robot base frame
Z_BASE_MIN = 0.185
X_BASE_MIN = -0.12051
Y_BASE_MIN = 0.28071

# gripper widths
GRIPPER_WIDTH_TARGET = 0.06 # in meters
GRIPPER_WIDTH_ORIGIN = 0.1 # in meters

# max block width
BLOCK_WIDTH = 0.035 # in meters

# fixed rotational position ensuring position is perpendicular to the plate
YAW = 0
PITCH = np.pi
ROLL = 0

PICK_AREA = Rectangle()
PLACE_AREA = Rectangle()
HOME_AREA = Triangle()
STOCK_AREA = Triangle()

PICK_AREA.xmin, PICK_AREA.xmax, PICK_AREA.ymin, PICK_AREA.ymax = -1, 8, 1, 5
PLACE_AREA.xmin, PLACE_AREA.xmax, PLACE_AREA.ymin, PLACE_AREA.ymax = 10, 16, -10, -1
HOME_AREA.v1, HOME_AREA.v2, HOME_AREA.v3 = (10, 1), (10, 4), (13, 1)
STOCK_AREA.v1, STOCK_AREA.v2, STOCK_AREA.v3 = (-3, 1), (-3, 4), (-6, 1)

VALID_REGIONS = [PICK_AREA, PLACE_AREA, HOME_AREA, STOCK_AREA]
