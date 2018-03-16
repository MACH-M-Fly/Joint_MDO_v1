import Structures.structAnalysis as struct_anal

import numpy as np


# Define tail boom parameters
boom_type = 'R'
width_o = 0.0254
width_i = 0.022225
boom_dim = (width_o, width_o, width_i, width_i)
boom_E = 68.9e9
boom_len = 0.9144

# Define loaded masses
masses_1 = [0.458, 0.912, 1.367, 1.823, 2.274, 2.725, 3.175, 3.627, 4.080, 4.532]

masses = [masses_1]

for i in range(len(masses)):
    print('Trial %d')

    for m in masses[i]:
        P = m * 9.807
        x_tail = np.linspace(0, boom_len, 1001)
        c_tail, I_tail = struct_anal.calcI(boom_type, boom_dim)
        M_tail, y_tail, sigma_tail = struct_anal.calcPointLoad(x_tail, boom_len, P, I_tail, boom_E, c_tail)
        print('P = {:0.5f} N\tD = {:.6e}'.format(P, max(y_tail)))

    print()
