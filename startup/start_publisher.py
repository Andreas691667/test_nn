from communication.rabbitmq import Rabbitmq
from startup.utils.config import load_config_w_setuptools
from time import sleep

import communication.protocol as protocol

class Publisher:
    def __init__(self) -> None:
        self.config = load_config_w_setuptools("startup.conf")
        self.rabbitmq_config = self.config["rabbitmq"]
        self.rabbitmq = Rabbitmq(**self.rabbitmq_config)
        self.rabbitmq.connect_to_server()
    
    def publish_4ever(self) -> None:
        i = 0
        while True:
            self.rabbitmq.send_message("numbers", str(i))
            print(f"Publisher send message {i}")
            i+=1
            sleep(3)
    
    def ctrl_msg_publish(self):
        while True:
            msg = {
                protocol.RobotArmStateKeys.READY: True,
            }
            self.rabbitmq.send_message(routing_key=protocol.ROUTING_KEY_STATE,
                                       message=msg)
            print(f"Publisher send message {msg}")
            sleep(1)
        

def start_publisher(ok_queue=None):
    publisher = Publisher()

    if ok_queue is not None:
        ok_queue.put("OK")

    publisher.ctrl_msg_publish()


if __name__ == '__main__':
    start_publisher()