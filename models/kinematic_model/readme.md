# Kinematic Model

This folder contains the code for the kinematic model of the robot. The kinematic model has two main functionalities; inverse kinematics and trajectory generation. Addionally, it can compute forward kinematics.

The kinematic model is implemented using the Robotics-Toolbox-for-Python library (RTB), for which the documentation can be found [in this link](https://petercorke.github.io/robotics-toolbox-python/).

## Contents
- [Kinematic Model](#kinematic-model)
  - [Contents](#contents)
  - [The kinematic model](#the-kinematic-model)
  - [Inverse Kinematics](#inverse-kinematics)
  - [Trajectory Generation](#trajectory-generation)


<!-- 1. [Inverse Kinematics](#inverse-kinematics): Given the desired end-effector position and orientation, the kinematic model computes the joint angles required to achieve this position.
2. [Trajectory Generation](#trajectory-generation): Given two joint positions and a time, the kinematic model generates a trajectory that moves the end-effector from the first position to the second position. -->

## The kinematic model
The kinematic model is implemented using the ```rtb.DHRobot``` class from the Robotics-Toolbox-for-Python library. The ```DHRobot``` class is used to represent a robot with Denavit-Hartenberg (DH) parameters. The DH-parameters are provided by Universal Robots in [this page](https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/) and are specified in the ```km_config.py``` file. 


## Inverse Kinematics
Given the desired spatial pose of the end effector $S=\{x_R, y_R, z_R, rx, ry, rz\}$ where $(x_R, y_R, z_R)$ is the position of the end effector and $(rx, ry, rz)$ is the orientation (yaw-pitch-roll) of the end effector, the inverse kinematics function ```compute_inverse_kinematics(P_S)``` computes the joint angles required to achieve this pose. It is also possible to provide the paramater ```wrist_rotation``` to specify the orientation of the wrist. This is useful when the gripper will collide with the object if the wrist is not rotated.

The function uses the [```ikine_LM``` function](https://petercorke.github.io/robotics-toolbox-python/IK/stubs/roboticstoolbox.robot.Robot.Robot.ikine_LM.html) to compute the joint angles, which is a Levenberg-Marquardt optimization-based inverse kinematics solver. If the inverse kinematics finds a solution, the function returns the joint angles as a numpy array. If the inverse kinematics does not find a solution, the function returns ```None```.

## Trajectory Generation
Given the starting joint position $J_0$, the end joint position $J_1$ and the time $t$ to move from $J_0$ to $J_1$, the trajectory generation function ```compute_trajectory(J0, J1, t)``` computes the joint angles required to move the end-effector from $J_0$ to $J_1$ in time $t$ using the [```jtraj``` function](https://petercorke.github.io/robotics-toolbox-python/arm_trajectory.html#roboticstoolbox.tools.trajectory.jtraj). The function returns a ```Trajectory``` object as described in [the documentation](https://petercorke.github.io/robotics-toolbox-python/arm_trajectory.html#roboticstoolbox.tools.trajectory.Trajectory).

## Forward Kinematics
Given the joint positions $\mathbf{\theta} \in  \mathbb{R}^6$, the function ```compute_forward_kinematics``` can compute the corresponding spatial pose. The return type is an SE(3) matrix $\in \mathbb{R}^{4\times 4}$. 