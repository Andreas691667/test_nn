import numpy as np
from spatialmath import SE3
from spatialmath.base import trnorm, transforms3d
import roboticstoolbox as rtb
import models.kinematic_model.km_config as km_config


class KinematicModel(rtb.DHRobot):
    """Kinematic Model of a robot specified by DH parameters"""

    def __init__(self):

        # initial guess vector for IK
        self.q0 = km_config.q0

        # time step value for trajectory generation
        self.time_step = km_config.dt

        # read DH parameters from config
        link1 = rtb.RevoluteMDH(*km_config.link1_dh)
        link2 = rtb.RevoluteMDH(*km_config.link2_dh)
        link3 = rtb.RevoluteMDH(*km_config.link3_dh)
        link4 = rtb.RevoluteMDH(*km_config.link4_dh)
        link5 = rtb.RevoluteMDH(*km_config.link5_dh)
        link6 = rtb.RevoluteMDH(*km_config.link6_dh)

        # initialize the robot
        super().__init__(
            [link1, link2, link3, link4, link5, link6], name=km_config.model_name
        )

    # region PUBLIC METHODS
    def compute_inverse_kinematics(self, spatial_pose, wrist_rotation : float=0.):
        """Compute the inverse kinematics for the UR3e robot arm given a spatial pose
        :param spatial_pose: The spatial pose of the robot arm (x, y, z, roll, pitch, yaw)
        :type np.array
        :param wrist_rotation: The rotation of the wrist
        :type float
        :returns: The joint positions of the robot arm (q1, q2, q3, q4, q5, q6)
        :rtype: np.array
        """
        se3_pose = self.__convert_to_se3(spatial_pose)
        q = self.__compute_inverse_kinematics(se3_pose)
        q = self.__fit_to_shortest_path(q)
        if wrist_rotation:
            q = self.__rotate_wrist(q, wrist_rotation)
        return q

    def compute_trajectory(self, start, end, t):
        """Compute the trajectory between two points in joint space
        :param start: The starting joint positions of the robot arm (q1, q2, q3, q4, q5, q6)
        :type np.array
        :param end: The ending joint positions of the robot arm (q1, q2, q3, q4, q5, q6)
        :type np.array
        :param t: The time to reach the end position
        :type float
        :returns: The trajectory of the robot arm
        :rtype rtb.Trajectory
        """
        no_steps = int(t / self.time_step)
        return rtb.jtraj(start, end, t=no_steps)
    
    def plot_trajectory(self, trajectory):
        """Plot the trajectory of the robot arm
        :param trajectory: The trajectory generated by the compute_trajectory method
        :type rtb.Trajectory
        """
        self.plot(trajectory, block=False)

    def compute_forward_kinematics (self, jps) -> list[np.ndarray] | np.ndarray:
        """ Compute forward kinematics
        :param jps: The joint positions list
        :returns: the spatial pose as an SE3 matrix
        """
        T =  self.fkine(jps).A
        return T

    # endregion

    # region PRIVATE METHODS
    def __compute_inverse_kinematics(self, T):
        """Compute IK given spatial pose matrix T
        :param T: The spatial pose matrix
        :type SE3
        :returns: The joint positions of the robot arm (q1, q2, q3, q4, q5, q6) if reachable
        :rtype np.array
        """
        sol = self.ikine_LM(T, q0=self.q0)

        if sol.success:
            return sol.q
        else:
            raise ValueError(f"Position \n {T} \n not reachable")

    def __convert_to_se3(self, spatial_pose):
        """Convert spatial pose to SE3 matrix
        :param spatial_pose: The spatial pose of the robot arm (x, y, z, roll, pitch, yaw)
        :type np.array
        :returns: The SE3 matrix
        :rtype SE3
        """
        x, y, z, roll, pitch, yaw = spatial_pose
        c_roll, s_roll = np.cos(roll), np.sin(roll)
        c_pitch, s_pitch = np.cos(pitch), np.sin(pitch)
        c_yaw, s_yaw = np.cos(yaw), np.sin(yaw)

        t = np.array(
            [
                [
                    c_yaw * c_pitch,
                    c_yaw * s_pitch * s_roll - c_roll * s_yaw,
                    c_yaw * s_pitch * c_roll + s_yaw * s_roll,
                    x,
                ],
                [
                    s_yaw * c_pitch,
                    s_yaw * s_pitch * s_roll + c_yaw * c_roll,
                    s_yaw * s_pitch * c_roll - c_yaw * s_roll,
                    y,
                ],
                [-s_pitch, c_pitch * s_roll, c_pitch * c_roll, z],
                [0, 0, 0, 1],
            ]
        )

        return SE3(trnorm(t))

    def __fit_to_shortest_path(self, q):
        """Force the joint positions to take the shortest path
        :param q: The joint positions of the robot arm (q1, q2, q3, q4, q5, q6)
        :type np.array
        :returns: The joint positions of the robot arm (q1, q2, q3, q4, q5, q6)
        :rtype np.array
        """
        if q[0] < 0:
            q[0] += 2 * np.pi

        if q[-1] < 0:
            q[-1] += 2 * np.pi

        return q

    def __rotate_wrist(self, q, rotation):
        """Rotate the wrist by 90 degrees
        :param q: The joint positions of the robot arm (q1, q2, q3, q4, q5, q6)
        :type np.array
        :param rotation: The rotation of the wrist
        :type float
        :returns: The joint positions of the robot arm with rotated q6 (q1, q2, q3, q4, q5, q6)
        :rtype np.array
        """
        q[-1] -= rotation
        return q