#!/usr/bin/env python

import torch
import torch.nn as nn
from torch.autograd import Function


from models.kinematic_model.kinematic_model import KinematicModel
from models.timing_model.timing_model import TimingModel
from models.spatial_model.spatial_model import SpatialModel
from models.robot_visualizer.robot_visualizer import RobotVisualizer
import task_specifications.tasks as tasks
import task_specifications.utils.operation_types as operation_types


km = KinematicModel()
tm = TimingModel()
sm = SpatialModel()
rv = RobotVisualizer()

# helper function to generate joint position given grid position
def grid_to_joint_position(grid_position):
    x, y, z = grid_position
    return km.compute_inverse_kinematics(sm.compute_spatial_pose(x, y, z))

def generate_timed_task_matrix(task, initial_grid_position):
    x, y, z = initial_grid_position
    start_joint_position = grid_to_joint_position((x, y, z))
    task_matrix = []
    for operation in task:
        if isinstance(operation, operation_types.Move):
            x_t, y_t, z_t = operation.x, operation.y, operation.table_distance
            joint_position = grid_to_joint_position((x_t, y_t, z_t))
            time = tm.compute_duration_between_jps(start_joint_position, joint_position)
            task_matrix.append([*start_joint_position, *joint_position, time])
            start_joint_position = joint_position
        elif isinstance(operation, operation_types.Grip):
            task_matrix.append([*start_joint_position, *start_joint_position, 0])
        elif isinstance(operation, operation_types.MoveGripper):
            task_matrix.append([*start_joint_position, *start_joint_position, 0])

    return task_matrix


# example task
task = tasks.two_blocks

# Define the model
class TimingOffsetModel(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(TimingOffsetModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


# Custom autograd function for km.compute_trajectory
class ComputeTrajectory(Function):
    @staticmethod
    def forward(ctx, start, end, t):
        start_np = start.detach().numpy()
        end_np = end.detach().numpy()
        t_scalar = t.item()
        trajectory_segment = km.compute_trajectory(start_np, end_np, t_scalar)
        result = torch.tensor(trajectory_segment.q, dtype=torch.float32)
        return result

    @staticmethod
    def backward(ctx, grad_output):
        # Implement the backward pass if needed
        return None, None, None


# Updated generate_trajectory function
def generate_trajectory(timed_task_matrix):
    trajectory = []
    for op in timed_task_matrix:
        start = op[:6]
        end = op[6:12]
        t = op[12]
        trajectory_segment = ComputeTrajectory.apply(start, end, t)
        trajectory.append(trajectory_segment)
    return torch.cat(trajectory, dim=0)


# Dummy functions for pad_sequence_to_match
def pad_sequence_to_match(seq1, seq2):
    max_len = max(seq1.size(0), seq2.size(0))
    padded_seq1 = torch.nn.functional.pad(seq1, (0, 0, 0, max_len - seq1.size(0)))
    padded_seq2 = torch.nn.functional.pad(seq2, (0, 0, 0, max_len - seq2.size(0)))
    return padded_seq1, padded_seq2


# Training loop
def train_model(
    model, criterion, optimizer, timed_task_matrix, trajectory_noisy, num_epochs=1000
):
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        output = model(timed_task_matrix)
        timed_task_matrix_with_offsets = timed_task_matrix.clone()
        timed_task_matrix_with_offsets[:, 12]  = timed_task_matrix_with_offsets[:, 12] + torch.relu(output[:,0])
        trajectory_with_offsets = generate_trajectory(timed_task_matrix_with_offsets)
        trajectory_with_offsets, trajectory_noisy = pad_sequence_to_match(
            trajectory_with_offsets, trajectory_noisy
        )
        loss = criterion(trajectory_with_offsets, trajectory_noisy)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}")
            print(f"Model output: {output[0].item()}")
            # print(f"Timed task matrix with offsets: {timed_task_matrix_with_offsets[:, 12]}")


# Check requires_grad for model parameters
model = TimingOffsetModel(input_size=13, hidden_size=64)
for name, param in model.named_parameters():
    print(f"{name}: requires_grad={param.requires_grad}")

# Train the model
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Dummy data
timed_task_matrix = torch.tensor(
    generate_timed_task_matrix(task, (0, 0, 0)), dtype=torch.float32
)
timed_task_matrix_noisy = timed_task_matrix.clone()
timed_task_matrix_noisy[:, 12] += abs(torch.randn_like(timed_task_matrix[:, 12]) * 0.1)
trajectory_noisy = (
    generate_trajectory(timed_task_matrix_noisy).clone().detach()
)

train_model(
    model, criterion, optimizer, timed_task_matrix, trajectory_noisy, num_epochs=100
)
