# import logging
import time
import sys

from startup.utils.config import load_config_w_setuptools
from dt.services.robot_visualization import RobotVisualization


def start_pt_visualization(ok_queue=None):
    # TODO implement logging
    # config_logger("logging.conf")
    # l = logging.getLogger("start_pt_visualization")
    config = load_config_w_setuptools("startup.conf")

    while True:
        try:
            rv = RobotVisualization(rmq_config=config["rabbitmq"])
            rv.setup()
            if ok_queue is not None:
                ok_queue.put("OK")
            rv.start_visualizing()
            time.sleep(7) # to allow time for port input
        except KeyboardInterrupt:
            rv.cleanup() # ensure that the visualization is stopped
            sys.exit(0)
        except Exception as exc:
            # l.error("The following exception occurred. Attempting to reconnect.")
            # l.error(exc)
            time.sleep(1.0)

if __name__ == '__main__':
    start_pt_visualization()
