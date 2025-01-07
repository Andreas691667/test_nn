import time

from startup.utils.config import load_config_w_setuptools
from dt.services.self_adaptation_manager import SelfAdaptationManager


def start_self_adaptation_manager(ok_queue=None):
    config = load_config_w_setuptools("startup.conf")

    while True:
        try:
            self_adaptation_manager = SelfAdaptationManager(
                rmq_config=config["rabbitmq"],
            )
            self_adaptation_manager.setup()
            if ok_queue is not None:
                ok_queue.put("OK")
            self_adaptation_manager.start()
        except KeyboardInterrupt:
            exit(0)
        except Exception as exc:
            # l.error("The following exception occurred. Attempting to reconnect.")
            # l.error(exc)
            time.sleep(1.0)


if __name__ == "__main__":
    start_self_adaptation_manager()
