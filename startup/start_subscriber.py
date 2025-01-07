from communication.rabbitmq import Rabbitmq
from startup.utils.config import load_config_w_setuptools

class Subscriber:
    def __init__(self) -> None:
        self.config = load_config_w_setuptools("startup.conf")
        self.rabbitmq_config = self.config["rabbitmq"]
        self.rabbitmq = Rabbitmq(**self.rabbitmq_config)
        self.rabbitmq.connect_to_server()
    
    def subscribe(self) -> None:
        self.rabbitmq.subscribe("numbers", self.on_numbers_callback)
        self.rabbitmq.start_consuming()
        
    def on_numbers_callback (self, ch, method, properties, body_json):
        print(f"Subscriber recieved message: {body_json}")

def start_subscriber(ok_queue=None):
    subscriber = Subscriber()

    if ok_queue is not None:
        ok_queue.put("OK")

    subscriber.subscribe()


if __name__ == '__main__':
    start_subscriber()