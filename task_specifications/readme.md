# Task specifications
This folder contains information on how the pick-and-place tasks are defined. 
Below is a video of the robot performing a pick-and-place task. The task consists of moving the robot to a specific location, gripping an object, moving the object to a new location, and releasing the object. The task is defined using the basic building blocks and operation sequences described below.

![](./example_movement.mp4)


# Contents
- [Task specifications](#task-specifications)
- [Contents](#contents)
  - [Basic building blocks](#basic-building-blocks)
  - [Operation sequences](#operation-sequences)
  - [Task construction](#task-construction)

## Basic building blocks
Within [operation_types.py](utils/operation_types.py) folder, you will find three basic building blocks that are used to define the tasks. These are:
- ```Move```: This operation type is used to move the robot to a specific location in the grid. A position is defined by a tuple (x,y) where $x,y\in G$ and the height above the plate specified by ```table_distance```. An optional parameter ```rotation``` can be used to specify the rotation of the gripper (defaults to 0).
- ```Grip```: This operation type is used to grip an object. 
- ```MoveGripper```: This operation type is used to move the gripper to a specific percentage of the gripper's range. The percentage is specified by the ```position``` parameter. The gripper's range is from 0.0 (fully open) to 1.0 (fully closed).

## Operation sequences
To avoid the need to define the same operation sequences multiple times, the [operation_sequences.py](utils/operation_sequences.py) file contains a set of predefined operation sequences. These sequences can be used to define the tasks more easily. The following operation sequences are available:
- ```move_and_grip```: This operation sequence is used to move the robot to a specific (x, y) location and grip an object. The rotation of the end-effector can be specified using the optional ```rotation``` parameter. The full sequence consists of the following operations:
  1. Move the robot to the specified (x, y) location (z is 1 so the arm is above the object).
  2. Move the robot down to the specified (x, y) location (z is 0 so the arm is at the object).
  3. Grip the object.
  4. Move the robot up to the specified (x, y) location (z is 1 so the arm is above the object).
- ```move_and_release```: This operation sequence is used to move the robot to a specific (x, y) location and release an object. The rotation of the end-effector can be specified using the optional ```rotation``` parameter. The full sequence consists of the following operations:
    1. Move the robot to the specified (x, y) location (z is 1 so the arm is above the target).
    2. Move the robot down to the specified (x, y) location (z is 0 so the arm is at the target).
    3. Release the object.
    4. Move the robot up to the specified (x, y) location (z is 1 so the arm is above the object).

Each operation sequence is simply a list of the basic building blocks (```Move```, ```Grip``` and ```Release```) defined above. The operation sequences can be used to define the tasks more easily.

## Task construction
The [tasks.py](tasks.py) file contains a set of predefined tasks using the two operation sequences described above. Take notice of the way the tasks are defined by unpacking the operation sequences using the ```*``` operator. This way, the operation sequences are expanded into the individual operations that make up the task. This makes the tasks specifications simple lists of the basic building blocks. 