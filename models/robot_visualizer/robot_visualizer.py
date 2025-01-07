import time
import subprocess
import zmq
import matplotlib.pyplot as plt
import itertools
import pathlib
import numpy as np
import models.robot_visualizer.rm_config as rm_config


class RobotVisualizer:
    """Class to manage the visualisation application"""

    def __init__(self, port = rm_config.port) -> None:

        # Path to the visualisation application
        self.application_path = str(pathlib.Path(__file__).parent.resolve()) + "\\" + rm_config.application_path

        # Initialize the application process
        self.app_process = None
        self.process_running = False
        self.socket = None
        self.port = port

        # Initialize the topic names
        self.topic_names = [
            "actual_q_0",
            "actual_q_1",
            "actual_q_2",
            "actual_q_3",
            "actual_q_4",
            "actual_q_5",
        ]

    def __initialize_socket(self):
        """Initializes the zmq socket"""
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.port}")

    def publish_joint_positions(self, joint_positions):
        """Publishes the joint positions on the visualisation application
        :param joint_positions: The joint positions of the robot arm (q1, q2, q3, q4, q5, q6)
        :type np.array"""

        for i in range(6):
            self.__publish_on_topic(self.topic_names[i], joint_positions[i])

    def visualize_trajectory(self, trajectory, time_step=0.05):
        """Visualizes the trajectory on the visualisation application
        :param trajectory: The trajectory of the robot arm
        :type np.array"""

        total_len = len(trajectory)
        for i, joint_position in enumerate(trajectory):
            self.publish_joint_positions(joint_position)
            print(f"\t\rVisualizing position [{i}/{total_len-1}]", end="", flush=True)
            time.sleep(time_step)

    def __publish_on_topic(self, topic, msg_data):
        """Publishes a message on a topic
        :param topic: The topic name
        :type str
        :param msg_data: The message data
        :type float"""
        self.socket.send_string(f"{topic} {msg_data}")

    def stop_visualization(self):
        """Stops the visualization application and the zmq socket"""
        if self.process_running:
            print("Stopping Visualization")
            self.socket.send_string("stop stop")
            if self.app_process is not None:
                self.app_process.kill()
            self.socket.close()
            self.process_running = False
        else:
            print("Application not running")

    def start_application(self):
        """Starts the visualization application"""
        if not self.process_running:
            self.__initialize_socket()
            self.process_running = True
            self.app_process = subprocess.Popen([self.application_path])
            print("Visualization Application Started")
        else:
            print("Application already running")

    def plot_trajectory_2d(self, trajectory, labels=None, joints=None, time_step=0.05):
        """Plot the trajectory of the robot arm
        :param trajectory: The trajectory or trajectories to plot
        :type rtb.Trajectory or np.array (or list of either)
        :param labels: Labels for each trajectory, optional
        :type labels: list or str, optional
        :param joints: List of joint indices to plot (e.g., [0, 1, 5]). Plots all joints if None.
        :type joints: list, optional
        :param time_step: Time step between points, optional
        :type time_step: float
        """
        # Ensure trajectory is a list for uniform processing
        if not isinstance(trajectory, list):
            trajectory = [trajectory]

        # If no labels provided, create default labels
        if labels is None:
            labels = [f"Trajectory {i+1}" for i in range(len(trajectory))]
        elif isinstance(labels, str):
            labels = [labels]

        # Ensure labels length matches the number of trajectories
        if len(labels) < len(trajectory):
            labels.extend(
                [f"Trajectory {i+1}" for i in range(len(labels), len(trajectory))]
            )

        # Use color cycle for distinguishing different trajectories
        color_cycle = itertools.cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

        # Define different line styles
        line_styles = itertools.cycle(["-", "--", "-.", ":"])

        if joints is None:
            joints = list(range(6))

        # Initialize figure and subplots, dynamically adjust number of subplots
        num_joints = len(joints)
        rows = (num_joints + 2) // 3  # Adjust number of rows based on selected joints
        cols = min(num_joints, 3)
        fig = plt.figure(figsize=(5 * cols, 5 * rows))
        subfigs = fig.subplots(rows, cols).flatten() if num_joints > 1 else [fig.subplots()]
          # Flatten to handle dynamic number of subplots

        # Plot each trajectory with corresponding label, color, and style using helper function
        for traj, label, color, style in zip(
            trajectory, labels, color_cycle, line_styles
        ):
            self.__plot_trajectory_2d(traj, time_step, subfigs, label, color, style, joints)

        plt.tight_layout()
        plt.show()

    def __plot_trajectory_2d(self, trajectory, time_step, subfigs, label, color, style, joints):
        """Helper function to plot a single trajectory"""
        # If trajectory is a trajectory object, extract q and t values
        if hasattr(trajectory, "q"):
            trajectory = trajectory.q
        if hasattr(trajectory, "t"):
            time_steps = trajectory.t
        else:
            time_steps = np.linspace(0, time_step * len(trajectory), len(trajectory))

        # ymin and ymax chosen for joints parameter
        ymin = trajectory[:, joints].min()
        ymax = trajectory[:, joints].max()

        # Loop through each joint (assuming 6 DOF)
        for plot_idx, joint in enumerate(joints):

            axs = subfigs[plot_idx]
            axs.plot(time_steps, trajectory[:, joint], label=label, color=color, linestyle=style)
            axs.set_title(f"q{joint}")
            axs.set_ylim([ymin - 0.1, ymax + 0.1])

            # Set axis labels and formatting
            axs.set_xlabel("Time [s]")
            axs.set_ylabel("Angle [rad]")

            # Set the appearance of the plot
            axs.set_facecolor("white")
            axs.spines["bottom"].set_color("black")
            axs.spines["top"].set_color("black")
            axs.spines["right"].set_color("black")
            axs.spines["left"].set_color("black")
            axs.grid(c="lightgray")

            # Add legend to each subplot
            axs.legend()
