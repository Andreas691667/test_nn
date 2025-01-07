from typing import Any

from communication.rabbitmq import Rabbitmq
import communication.protocol as protocol
from models.timing_model.timing_model import TimingModel
from models.kinematic_model.kinematic_model import KinematicModel
from models.spatial_model.spatial_model import SpatialModel


class SelfAdaptationManager():
    """description.
    :param name: description
    """

    def __init__(
        self,
        rmq_config,
    ):
        # need two rmqs as pika is not thread safe
        self.rmq = Rabbitmq(**rmq_config)

        # -- Models
        self.timing_model = TimingModel()
        self.kinematic_model = KinematicModel()
        self.spatial_model = SpatialModel()
        # --

        self.monitor_data = None

    def setup(self):
        """Setup rmq subscriptions and start the state publishing thread"""
        self.rmq.connect_to_server()

        self.rmq.subscribe(
            routing_key=protocol.ROUTING_KEY_STATE,  # For PT messages
            on_message_callback=self.__analyse_data,
        )

    def start(self):
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

    def __analyse_data(self, ch, method, properties, body_json):
        """Handle dt messages"""
        print("DT received pt message:", body_json)  # TODO: Implement logging
        fault_type = None
        if (fault_type): self.__plan(fault_type)

    
    def __plan (self, analysis_result: Any) -> None:
        """Plans a task based on analysis result
        :param analysis_result: the analysis result
        """
        plan = None
        # Do planning ->

        # execute
        self.__execute(plan)
        

    def __execute (self, plan: Any) -> None:
        """Executes a task
        :param plan: the plan to be executed  
        """
        self.rmq.send_message(protocol.ROUTING_KEY_DT_MSG, message=plan)