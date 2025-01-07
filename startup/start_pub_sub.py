from startup.utils.start_as_daemon import start_as_daemon
from startup.start_docker_rabbitmq import start_docker_rabbitmq
from startup.start_publisher import start_publisher
from startup.start_subscriber import start_subscriber

if __name__ == '__main__':
    start_docker_rabbitmq()
    start_as_daemon(start_publisher)
    start_as_daemon(start_subscriber)
    