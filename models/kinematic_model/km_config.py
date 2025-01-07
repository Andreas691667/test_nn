import numpy as np

model_name = "UR3e"

# DH parameters
link1_dh = [0.15185, 0, 0]
link2_dh = [0, 0, np.pi / 2]
link3_dh = [0, -0.24355, 0]  # changed a to negative
link4_dh = [0.13105, -0.2132, 0]  # changed a to negative
link5_dh = [0.08535, 0, np.pi / 2]
link6_dh = [0.0921, 0, -np.pi / 2]

# initial guess vector
q0 = [(3 * np.pi) / 2, -0.66, 0.76, -np.pi / 2, -np.pi / 2, 2.35]

# time step
dt = 0.05

# TODO Move the fixed rotational component here