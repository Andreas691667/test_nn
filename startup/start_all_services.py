from startup.utils.start_as_daemon import start_as_daemon
from startup.start_docker_rabbitmq import start_docker_rabbitmq
from startup.start_controller import start_controller
from startup.start_pt_visualization import start_pt_visualization
from startup.start_pt_mockup import start_robot_arm_mockup
from startup.start_self_adaptation import start_self_adaptation_manager

if __name__ == '__main__':
    start_docker_rabbitmq()
    start_as_daemon(start_pt_visualization)
    start_as_daemon(start_controller)
    start_as_daemon(start_robot_arm_mockup)
    start_as_daemon(start_self_adaptation_manager)
    