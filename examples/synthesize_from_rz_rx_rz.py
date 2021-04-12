#!/usr/bin/env python3

try:
    import numpy as np
    import scipy as sp
    from scipy.stats import unitary_group
    import cirq
except ImportError:
    print('Install extra dependencies:')
    print('    python3 -m pip install scipy "cirq~=0.10.0"')
    print()
    raise
from bloch_sphere.animate_bloch_compare import main

# Random unitary gate
seed = 18
u = unitary_group.rvs(2, random_state=seed)

# Compute Bloch rotation axis and angle
axis_angle = cirq.linalg.axis_angle(u)
print('Axis angle:', axis_angle)
#      Axis angle: 0.366*π around -0.233*X+0.831*Y-0.505*Z

# Decompose into Rz, Ry, Rz
angles = np.array(
    cirq.linalg.deconstruct_single_qubit_matrix_into_angles(u))
# Convert to Rz, Rx, Rz
angles[0] -= np.pi/2
angles[2] += np.pi/2
print('Rz, Rx, Rz angles (radians):', angles)
#      Rz, Rx, Rz angles (radians): [4.12326921 0.97622252 1.52745046]

# Show the circuit
q = cirq.LineQubit(0)
circuit = cirq.Circuit(
    cirq.rz(angles[0])(q),
    cirq.rx(angles[1])(q),
    cirq.rz(angles[2])(q),
)
print(circuit)
#     0: ───Rz(1.31π)───Rx(0.311π)───Rz(0.486π)───

# Check circuit
assert cirq.equal_up_to_global_phase(u, cirq.unitary(circuit))

# Generate animation
main('random_as_zxz',
     # Left gate
     [f'custom;{axis_angle.axis[0]};{axis_angle.axis[1]};'
      f'{axis_angle.axis[2]};{axis_angle.angle/np.pi};Random'],
     # Right gates
     [f'custom;0;0;1;{angles[0]/np.pi};Rz({angles[0]/np.pi:.3f}π)',
      f'custom;1;0;0;{angles[1]/np.pi};Rx({angles[1]/np.pi:.3f}π)',
      f'custom;0;0;1;{angles[2]/np.pi};Rz({angles[2]/np.pi:.3f}π)'],
     # Circuit diagram
     r'& \gate{U} & \qw & \push{=} & & \gate{R_Z} & \gate{R_X} & \gate{R_Z} & '
     r'\qw',
     # Circuit equation
     #r'$U\ket{\psi}=R_Z R_X R_Z\ket{\psi}$',
     mp4=False,
     fps=20,
     preview=False,
)
