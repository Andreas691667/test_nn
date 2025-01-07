from task_specifications.utils.operation_sequences import move_and_grip, move_and_release

one_block = [
    *move_and_grip(1, 1),
    *move_and_release(13, -5)
]

two_blocks = [
    *move_and_grip(0, 1),
    *move_and_release(13, -5),
    *move_and_grip(3, 1),
    *move_and_release(12, -3)
]

square = [
    *move_and_grip(-1, 1),
    *move_and_release(12, -7),
    *move_and_grip(-1, 2),
    *move_and_release(12, -6),
    *move_and_grip(2, 1),
    *move_and_release(12, -5),
    *move_and_grip(2, 2),
    *move_and_release(13, -5),
    *move_and_grip(5, 1),
    *move_and_release(14, -5),
    *move_and_grip(5, 2),
    *move_and_release(14, -6),
    *move_and_grip(8, 1),
    *move_and_release(14, -7),
    *move_and_grip(8, 2),
    *move_and_release(13, -7)
]
