import logging
from typing import Any, Dict
import time

from communication.rabbitmq import Rabbitmq
import communication.protocol as protocol
from models.spatial_model.spatial_model import SpatialModel
from models.kinematic_model.kinematic_model import KinematicModel
import task_specifications.tasks as tasks
import task_specifications.utils.operation_types as operation_types


class CtrlMessage:
    """Factory for creating control message dictionaries to be sent to the robot arm."""

    @staticmethod
    def movej(joint_positions: Any) -> Dict[str, Any]:
        """Creates a control message for a Move operation."""
        return {
            protocol.CtrlMsgKeys.TYPE: protocol.CtrlMsgFields.MOVEJ,
            protocol.CtrlMsgKeys.JOINT_POSITIONS: joint_positions,
        }

    @staticmethod
    def grip() -> Dict[str, Any]:
        """Creates a control message for a Grip operation."""
        return {
            protocol.CtrlMsgKeys.TYPE: protocol.CtrlMsgFields.GRIP,
        }

    @staticmethod
    def move_gripper(position: float) -> Dict[str, Any]:
        """Creates a control message for a MoveGripper operation."""
        return {
            protocol.CtrlMsgKeys.TYPE: protocol.CtrlMsgFields.MOVE_GRIPPER,
            protocol.CtrlMsgKeys.GRIPPER_POSITION: position,
        }
    @staticmethod
    def abort_operation() -> Dict[str, Any]:
        """Creates a control message for an AbortOperation operation."""
        return {
            protocol.CtrlMsgKeys.TYPE: protocol.CtrlMsgFields.ABORT_OPERATION,
        }


class Controller:
    """Controller class that manages the task stack and sends control messages to the robot arm.
    Controller also responds to messages from the DT and PT.
    :param rmq_config: Rabbitmq configuration
    :param task_spec_name: Name of the task specification to be used"""

    def __init__(self, rmq_config, task_spec_name):
        self.logger = logging.getLogger("Controller")

        self.rmq = Rabbitmq(**rmq_config)
        self.task_stack: list = getattr(tasks, task_spec_name)
        self.operation_id = 0

        self.spatial_model = SpatialModel()
        self.kinematic_model = KinematicModel()

    def setup(self):
        """Setup rmq subscriptions"""
        self.rmq.connect_to_server()
        self.rmq.subscribe(
            routing_key=protocol.ROUTING_KEY_DT_MSG,  # For dt messages
            on_message_callback=self.__update_task_stack,
        )
        self.rmq.subscribe(
            routing_key=protocol.ROUTING_KEY_STATE,  # For pt messages
            on_message_callback=self.__execute_task,
        )

    def start_controller(self):
        """Start consuming messages"""
        try:
            self.task_stack.reverse()  # Reverse the task stack to pop from the end
            self.rmq.start_consuming()
        except Exception:
            self.logger.exception("Error while consuming messages")
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.rmq.close()

    def __update_task_stack(self, ch, method, properties, body_json):
        """Update the task stack based on the received message"""

        msg_type = body_json[protocol.DTMsgKeys.TYPE]

        if msg_type == protocol.DTMsgFields.ADD:
            # Add the new task to the task stack
            self.task_stack.extend(body_json[protocol.DTMsgKeys.TASK_STACK])
        elif msg_type == protocol.DTMsgFields.REPLACE:
            # Replace the current task stack with the new task stack
            self.task_stack = body_json[protocol.DTMsgKeys.TASK_STACK]

        # initialize robot by aborting any ongoing operation
        self.__send_ctrl_msg(CtrlMessage.abort_operation())

        self.logger.debug("Performed <%s> operation on task stack", msg_type)

    def __execute_task(self, ch, method, properties, body_json):
        """Execute the next operation in the task if the robot arm is ready"""
        # Check if the task stack is empty
        if not self.task_stack:
            self.logger.info("Task stack is empty")

        # If the robot is ready to peform a new task
        elif (
            body_json[protocol.RobotArmStateKeys.READY]
            and self.operation_id == body_json[protocol.RobotArmStateKeys.OPERATION_ID]
        ):
            self.__execute_next_operation()

    def __execute_next_operation(self):
        """Execute the next operation in the task stack"""
        next_operation = self.task_stack.pop()
        self.operation_id += 1
        ctrl_message = None
        if isinstance(next_operation, operation_types.Move):
            # convert using spatial model
            spatial_position = self.spatial_model.compute_spatial_pose(
                next_operation.x, next_operation.y, next_operation.table_distance
            )

            joint_positions = (
                self.kinematic_model.compute_inverse_kinematics(
                    spatial_position, next_operation.rotation
                )
            ).tolist()

            ctrl_message = CtrlMessage.movej(joint_positions)

        elif isinstance(next_operation, operation_types.Grip):
            ctrl_message = CtrlMessage.grip()

        elif isinstance(next_operation, operation_types.MoveGripper):
            ctrl_message = CtrlMessage.move_gripper(next_operation.position)
        else:
            self.logger.error("Invalid operation type %s", type(next_operation))
            return

        self.__send_ctrl_msg(ctrl_message)
    
    def __send_ctrl_msg(self, ctrl_msg):
        """Send a control message to the robot arm"""
        ctrl_msg[protocol.CtrlMsgKeys.OPERATION_ID] = self.operation_id
        self.rmq.send_message(
            routing_key=protocol.ROUTING_KEY_CTRL, message=ctrl_msg
        )
        self.logger.debug("Sent control message %s:", ctrl_msg)
        print("Sent control message %s:", ctrl_msg)
