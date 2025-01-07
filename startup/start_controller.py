# import logging
import time

from startup.utils.config import load_config_w_setuptools
from physical_twin.controller.controller import Controller


def start_controller(ok_queue=None):
    # TODO implement logging
    # config_logger("logging.conf")
    # l = logging.getLogger("start_controller")
    config = load_config_w_setuptools("startup.conf")

    while True:
        try:
            controller = Controller(rmq_config=config["rabbitmq"], 
                                    task_spec_name=config["physical_twin"]["controller"]["task_specification"])
            controller.setup()
            if ok_queue is not None:
                ok_queue.put("OK")
            controller.start_controller()
        except KeyboardInterrupt:
            exit(0)
        except Exception as exc:
            # l.error("The following exception occurred. Attempting to reconnect.")
            # l.error(exc)
            time.sleep(1.0)

if __name__ == '__main__':
    start_controller()
