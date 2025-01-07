import json

ENCODING = "ascii"

### ROUTING KEYS
ROUTING_KEY_STATE = "robotarm.pt.state"
ROUTING_KEY_DT_MSG = "robotarm.dt.msg"
ROUTING_KEY_CTRL = "robotarm.ctrl"

### MESSAGES
class CtrlMsgKeys():
    OPERATION_ID = "operation_id"
    TYPE = "type"
    JOINT_POSITIONS = "joint_positions"
    GRIPPER_POSITION = "gripper_position"

class CtrlMsgFields():
    MOVEJ = "MoveJ"
    GRIP = "Grip"
    MOVE_GRIPPER = "MoveGripper"
    ABORT_OPERATION = "abort_operation"

class DTMsgKeys():
    TYPE = "type"
    TASK_STACK = "task_stack"

class DTMsgFields():
    ADD = "Add"
    REPLACE = "Replace"

class RobotArmStateKeys():
    OPERATION_ID = "operation_id"
    READY = "ready"
    ACTUAL_Q = "actual_q"
    ACTUAL_QD = "actual_qd"
    TIMESTAMP = "timestamp"
    OUTPUT_BIT_REGISTER_65 = "output_bit_register_65" # start bit
    OUTPUT_BIT_REGISTER_66 = "output_bit_register_66" # grip detected


### LEGACY
ROUTING_KEY_UPDATE_CTRL_PARAMS = "incubator.update.open_loop_controller.parameters"
ROUTING_KEY_UPDATE_CLOSED_CTRL_PARAMS = "incubator.update.closed_loop_controller.parameters"
ROUTING_KEY_CONTROLLER = "incubator.record.controller.state"
ROUTING_KEY_HEATER = "incubator.hardware.gpio.heater.on"
ROUTING_KEY_FAN = "incubator.hardware.gpio.fan.on"


def convert_str_to_bool(body):
    if body is None:
        return None
    else:
        return body.decode(ENCODING) == "True"


def encode_json(object):
    return json.dumps(object).encode(ENCODING)


def decode_json(bytes):
    return json.loads(bytes.decode(ENCODING))


def from_ns_to_s(time_ns):
    return time_ns / 1e9


def from_s_to_ns(time_s):
    return int(time_s * 1e9)


def from_s_to_ns_array(time_s):
    ns_floats = time_s * 1e9
    ns_ints = ns_floats.astype(int)
    return ns_ints
