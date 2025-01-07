# import logging
import time

from startup.utils.config import load_config_w_setuptools
from physical_twin.robot_arm_mockup.robot_arm_mockup import RobotArmMockup


def start_robot_arm_mockup(ok_queue=None):
    # TODO implement logging
    # config_logger("logging.conf")
    # l = logging.getLogger("start_robot_arm_mockup")
    config = load_config_w_setuptools("startup.conf")

    while True:
        try:
            robotarm = RobotArmMockup(
                rmq_config=config["rabbitmq"],
                initial_q=config["physical_twin"]["robot"]["initial_q"],
                missing_blocks=config["fault_injection"]["missing_blocks"],
                speedup=config["physical_twin"]["robot"]["speedup"],
                publish_freq=config["physical_twin"]["robot"]["publish_frequency"],
            )
            robotarm.setup()
            if ok_queue is not None:
                ok_queue.put("OK")
            robotarm.start_robot_arm_mockup()
        except KeyboardInterrupt:
            exit(0)
        except Exception as exc:
            # l.error("The following exception occurred. Attempting to reconnect.")
            # l.error(exc)
            time.sleep(1.0)


if __name__ == "__main__":
    start_robot_arm_mockup()
