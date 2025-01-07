# Physical Twin Mockup

This folder contains the scripts that are used to simulate the behavior of the UR3e robot arm and its controller. 

# Contents

- [Physical Twin Mockup](#physical-twin-mockup)
- [Contents](#contents)
- [Controller](#controller)
- [Robot arm mockup](#robot-arm-mockup)

# Controller

The controller in [controller.py](/physical_twin_mockup/controller/controller.py) is responsible for sending the different commands to the robot arm as described in the [task specification readme](/task_specifications/readme.md/). The logic is quite simple and is based on the following steps:

1. Initialize the connection to the robot arm, i.e. listen for incoming messages from the robot arm.
2. If the message says that the robot arm is ready, pop the next command from the task stack and send it to the robot arm.
3. If the message says that the robot arm has completed the command, pop the next command from the task stack and send it to the robot arm.
4. If the task stack is empty, the robot arm is done with the task and the controller can be stopped.

The controller also listens for incoming messages from the DT, which can be used to alter the task stack. There are two different operations that can be performed on the task stack:

1. ```ADD```: Add a stack of commands to the task stack.
2. ```REPLACE```: Replace the current task stack with a new stack of commands.

The DT messages are sent via the routing key ```ROUTING_KEY_DT_MSG``` (see [protocol.py](/communication/protocol.py)). 

The following parameters can be configured in a [startup file](/startup/startup.conf):

- ```rmq_config```: The RabbitMQ configuration.
- ```task_spec```: The task specification as defined in [tasks.py](/task_specifications/tasks.py).

# Robot arm mockup

The robot arm mockup in [robot_arm_mockup.py](/physical_twin_mockup/robot_arm_mockup/robot_arm_mockup.py) is responsible for simulating the behavior of the robot arm. The robot arm mockup listens for incoming messages from the controller and publishes it state via the routing key ```ROUTING_KEY_STATE```. 

The robot arm mockup can be configured in a [startup file](/startup/startup.conf):

- ```rmq_config```: The RabbitMQ configuration.
- ```initial_q```: The initial joint angles of the robot arm.
- ```missing_blocks```: The number of missing blocks from the task specification. This is used to simulate the behavior of the robot arm when it is not able to pick up a block from the plate due to a missing block.
- ```speedup```: The speedup factor of the robot arm.
- ```publish_freq```: The frequency at which the robot arm publishes its state.