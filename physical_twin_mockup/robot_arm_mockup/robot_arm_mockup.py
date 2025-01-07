import threading
import time
from queue import Queue, Empty
import numpy as np

from communication.rabbitmq import Rabbitmq
import communication.protocol as protocol
from models.timing_model.timing_model import TimingModel
from models.kinematic_model.kinematic_model import KinematicModel
from models.spatial_model.spatial_model import SpatialModel
import models.kinematic_model.km_config as km_config


class RobotArmMockup:
    """Mockup class for the robot arm.
    :param rmq_config: Rabbitmq configuration
    :param speedup: Speedup factor for the robot arm
    :param publish_freq: Frequency at which the state is published"""

    def __init__(
        self,
        rmq_config,
        initial_q,
        missing_blocks,
        speedup=1.0,
        publish_freq=20,
    ):
        # need two rmqs as pika is not thread safe
        self.rmq_out = Rabbitmq(**rmq_config)
        self.rmq_in = Rabbitmq(**rmq_config)

        self.timing_model = TimingModel()
        self.kinematic_model = KinematicModel()
        self.spatial_model = SpatialModel()

        self.operation_id = 0

        self.initial_q = initial_q
        
        # -- Fault detection
        self.last_jps = None # Used in grip to check the current position
        self.missing_blocks = missing_blocks
        self.missing_blocks_spatial_poses = self.__compute_spatial_poses_of_missing_blocks()
        # --

        self.speedup = speedup
        self.publish_interval = 1.0 / (publish_freq * speedup)
        self.state = {}

        self.grip_block_time = 0.7
        self.full_move_time = 1.5

        self.update_queue = Queue(maxsize=1)
        self.state_pub_thread = threading.Thread(
            target=self.__publish_state_loop, daemon=True
        )
        self.stop_pub_event = threading.Event()

    def setup(self):
        """Setup rmq subscriptions and start the state publishing thread"""
        self.rmq_out.connect_to_server()
        self.rmq_in.connect_to_server()

        self.rmq_in.subscribe(
            routing_key=protocol.ROUTING_KEY_CTRL,  # For control messages
            on_message_callback=self.__handle_ctrl_msg,
        )

        self.__init_state()
        self.state_pub_thread.start()

    def start_robot_arm_mockup(self):
        """Start consuming messages from the rmq"""
        try:
            self.rmq_in.start_consuming()
        except Exception as e:
            print(e)
            self.cleanup()

    def cleanup(self):
        """Stop the state publishing thread and rmq"""
        self.stop_pub_event.set()
        self.state_pub_thread.join()
        self.rmq_in.close()
        self.rmq_out.close()

    def __init_state(self):
        """Initialize the state dictionary"""
        self.state = {
            protocol.RobotArmStateKeys.READY: True,
            protocol.RobotArmStateKeys.ACTUAL_Q: self.initial_q,
            protocol.RobotArmStateKeys.ACTUAL_QD: [0] * 6,
            protocol.RobotArmStateKeys.TIMESTAMP: 0.0,
            protocol.RobotArmStateKeys.OUTPUT_BIT_REGISTER_65: False,
            protocol.RobotArmStateKeys.OUTPUT_BIT_REGISTER_66: False,
            protocol.RobotArmStateKeys.OPERATION_ID: self.operation_id,
        }

    def __handle_ctrl_msg(self, ch, method, properties, body_json):
        """Handle control messages"""
        print("Received control message:", body_json)  # TODO: Implement logging
        self.operation_id = body_json[protocol.CtrlMsgKeys.OPERATION_ID]

        if body_json[protocol.CtrlMsgKeys.TYPE] == protocol.CtrlMsgFields.MOVEJ:
            self.__move(
                body_json[protocol.CtrlMsgKeys.JOINT_POSITIONS],
            )
        elif body_json[protocol.CtrlMsgKeys.TYPE] == protocol.CtrlMsgFields.GRIP:
            self.__grip()
        elif (
            body_json[protocol.CtrlMsgKeys.TYPE] == protocol.CtrlMsgFields.MOVE_GRIPPER
        ):
            self.__move_gripper(body_json[protocol.CtrlMsgKeys.GRIPPER_POSITION])
        elif (
            body_json[protocol.CtrlMsgKeys.TYPE] == protocol.CtrlMsgFields.ABORT_OPERATION
        ):
            self.__abort_operation()

        # add operation_id to the state
        self.update_queue.put({protocol.RobotArmStateKeys.OPERATION_ID: self.operation_id})

    def __move(self, target_jps):
        """Move the robot arm to the specified position"""
        self.update_queue.put({protocol.RobotArmStateKeys.READY: False})

        start_pos = self.state[protocol.RobotArmStateKeys.ACTUAL_Q]

        duration = (
            self.timing_model.compute_duration_between_jps(start_pos, target_jps)
            / self.speedup
        )
        trajectory = self.kinematic_model.compute_trajectory(
            start_pos, target_jps, duration
        )

        for jp, qd in zip(trajectory.q, trajectory.qd):
            self.update_queue.put(
                {
                    protocol.RobotArmStateKeys.READY: False,
                    protocol.RobotArmStateKeys.ACTUAL_Q: jp.tolist(),
                    protocol.RobotArmStateKeys.ACTUAL_QD: qd.tolist(),
                }
            )

            time.sleep(km_config.dt)

        self.last_jps = target_jps
        self.update_queue.put({protocol.RobotArmStateKeys.READY: True})

    def __grip(self):
        """Grip the object"""
        self.update_queue.put({protocol.RobotArmStateKeys.READY: False})

        # If there is not a block at the current position
        if self.__is_block_missing():
            time.sleep((self.full_move_time * 2) / self.speedup)

        # If there is a block at the current position
        else:
            time.sleep(self.grip_block_time / self.speedup)
            self.update_queue.put(
                {
                    protocol.RobotArmStateKeys.READY: True,
                    protocol.RobotArmStateKeys.OUTPUT_BIT_REGISTER_66: True,
                }
            )

    def __move_gripper(self, position):
        """Move gripper to position"""
        self.update_queue.put({protocol.RobotArmStateKeys.READY: False})
        time.sleep((self.full_move_time * position) / self.speedup)
        self.update_queue.put(
            {
                protocol.RobotArmStateKeys.READY: True,
                protocol.RobotArmStateKeys.OUTPUT_BIT_REGISTER_66: False,
            }
        )

    def __abort_operation(self):
        """Abort the current operation"""
        self.update_queue.put({protocol.RobotArmStateKeys.READY: True})

    def __publish_state_loop(self):
        """Publish the robot arm state at a fixed interval"""
        while not self.stop_pub_event.is_set():
            try:
                new_state = self.update_queue.get(timeout=0.001)
                self.state.update(new_state)
            except Empty:
                pass  # No new state to publish, use the last state

            # update timestamp
            self.state[protocol.RobotArmStateKeys.TIMESTAMP] += self.publish_interval

            self.rmq_out.send_message(protocol.ROUTING_KEY_STATE, self.state)
            time.sleep(self.publish_interval)

    def __is_block_missing(self) -> bool:
        """Checks the block_setup in startup.conf["physical_twin"] for any match with the current position.
        returns: if there is a block at the posittion (true) or not (false)
        """
        T = self.kinematic_model.compute_forward_kinematics(self.last_jps)
        xyz_current = T[:3, 3]
        xyz_missing_blocks = [sp_block[:3] for sp_block in self.missing_blocks_spatial_poses]

        for _, xyz_missing_block in enumerate(xyz_missing_blocks):
            if np.allclose(xyz_missing_block, xyz_current):
                return True

        return False

    def __compute_spatial_poses_of_missing_blocks(self) -> list[list]:
        """Converts the grid positions from the block setup into spatial poses to be used for fault injection.
        returns: the corresponding spatial poses
        """
        spatial_poses = []
        for _, (x, y) in enumerate(self.missing_blocks):
            spatial_poses.append(self.spatial_model.compute_spatial_pose(x, y))
        return spatial_poses
