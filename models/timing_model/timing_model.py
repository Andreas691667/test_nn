# Internal packages
from models.timing_model.tm_custom_types import *
from models.timing_model.tm_config import *

# External packages
import numpy as np


class TimingModel:
    """This model models the duration between two joint positions, 
    assuming a trapezoidal or triangular timescaling of the movement."""

    def __init__(self) -> None:
        pass

    def compute_duration_between_jps(self, start_jp, end_jp) -> float:
        """Models durations between joint positions"""
        MAXIMUM_VELOCITY_RAD = np.deg2rad(MAXIMUM_VELOCITY)
        ACCELERATION_RAD = np.deg2rad(ACCELERATION)

        # Compute time scaling: Trapezoid or Triangular
        leading_axis_dist: float = max(
            np.abs(np.subtract(np.array(start_jp), np.array(end_jp)))
        )
        ts: time_scaling = (
            trapezoidal
            if leading_axis_dist >= MAXIMUM_VELOCITY_RAD**2 / ACCELERATION_RAD
            else triangular
        )

        # compute value depending on timescaling
        if ts == trapezoidal:
            return (
                ACCELERATION_RAD * leading_axis_dist + MAXIMUM_VELOCITY_RAD**2
            ) / (ACCELERATION_RAD * MAXIMUM_VELOCITY_RAD)
        else:
            return 2 * np.sqrt(leading_axis_dist / abs(ACCELERATION_RAD))
