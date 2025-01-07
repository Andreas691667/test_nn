from communication.rabbitmq import Rabbitmq
import communication.protocol as protocol
import models.robot_visualizer.robot_visualizer as rv


class RobotVisualization:
    """Class for sending robot position to the robot visualizer.
    :param rmq_config: Rabbitmq configuration"""

    def __init__(self, rmq_config):
        self.rmq = Rabbitmq(**rmq_config)
        self.visualizer = rv.RobotVisualizer()

    def setup(self):
        """Setup rmq subscriptions and start app"""
        self.rmq.connect_to_server()
        self.rmq.subscribe(
            routing_key=protocol.ROUTING_KEY_STATE,
            on_message_callback=self.__update_robot_position,
        )
        self.visualizer.start_application()


    def start_visualizing(self):
        """Start consuming messages from the RabbitMQ server."""
        try:
            self.rmq.start_consuming()
        except Exception:
            self.cleanup()

    def cleanup(self):
        """Cleanup the RabbitMQ connection and shutdown app."""
        self.visualizer.stop_visualization()
        self.rmq.close()

    def __update_robot_position(self, ch, method, properties, body):
        """Callback function for updating the robot position in the robot visualizer."""
        joint_position = body[protocol.RobotArmStateKeys.ACTUAL_Q]
        self.visualizer.publish_joint_positions(joint_position)
