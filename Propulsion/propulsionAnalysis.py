# python stantdard libraries
from __future__ import division

# addition python libraries
import numpy as np

# open MDAO libraries
from openmdao.api import Component

# Import self-created components
from APCdat_parser import createKriging


# Change the name of your componenet here
class propulsionAnalysis(Component):
    """
        Propulsion Analysis: Uses the current iteration of the aircraft, performances
        "input analysis name" analysis
        Inputs:
            - Aircraft_Class: Input aircraft instance
            - Design variables: These will be modified based on new MDO iteration
        Outputs:
            - Aircraft_Class: Output and modified aircraft instance
    """

    def __init__(self, ac):
        super(propulsionAnalysis, self).__init__()

        # Input instance of aircraft - before modification
        self.add_param('in_aircraft', val=ac, desc='Input Aircraft Class')

        # Output instance of aircaft - after modification
        self.add_output('out_aircraft', val=ac, desc='Output Aircraft Class')

        # Initialize Kriging Model
        self.model = createKriging([8, 11], [5, 9], [1000, 10000], 'exponential')

    def solve_nonlinear(self, params, unknowns, resids):
        # Used passed in instance of aircraft
        AC = params['in_aircraft']

        # Calculate battery parameters
        # Set it such that the only in increments of 3.7 V
        total_Voltage = AC.propulsion.cellNum * 3.7 * .8

        RPM = AC.propulsion.motorKV * total_Voltage
        # Calcualte thrust curve
        coeff1Model = self.model['coeff1'][0]
        coeff2Model = self.model['coeff2'][0]
        coeff3Model = self.model['coeff3'][0]
        coeff4Model = self.model['coeff4'][0]
        coeff5Model = self.model['coeff5'][0]
        coeff1ModelQ = self.model['coeff1Q'][0]
        coeff2ModelQ = self.model['coeff2Q'][0]
        coeff3ModelQ = self.model['coeff3Q'][0]
        coeff4ModelQ = self.model['coeff4Q'][0]
        coeff5ModelQ = self.model['coeff5Q'][0]

        coeff1T, ss = coeff1Model.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff2T, ss = coeff2Model.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff3T, ss = coeff3Model.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff4T, ss = coeff4Model.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff5T, ss = coeff5Model.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff1Q, ss = coeff1ModelQ.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff2Q, ss = coeff2ModelQ.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff3Q, ss = coeff3ModelQ.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff4Q, ss = coeff4ModelQ.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)
        coeff5Q, ss = coeff5ModelQ.execute('points', AC.propulsion.diameter, AC.propulsion.pitch, RPM)

        thrust_Curve = [coeff1T, coeff2T, coeff3T, coeff4T, coeff5T]
        #torque_Curve = [coeff1Q, coeff2Q, coeff3Q, coeff4Q, coeff5Q]

        AC.propulsion.setThrustCurve(thrust_Curve)

        # Calculate max current
        speeds = np.linspace(0.0, 13.0,100)
        torqueActual = []
        for speed in speeds:
            torqueActual.append(abs(
                speed ** 4 * coeff1Q + speed ** 3 * coeff2Q + speed ** 2 * coeff3Q + speed * coeff4Q + coeff5Q))

        maxTorque = np.amax(torqueActual)
        KT = 1.0 / AC.propulsion.motorKV
        maxCurrent = maxTorque / KT
        AC.propulsion.escCur = maxCurrent * 1.1  # Provide 30% margin

        print('\n######  Propulsion Analysis #######')
        print('Motor KV: %.3f ' % (AC.propulsion.motorKV))
        print('Prop Diam: %.3f In' % (AC.propulsion.diameter))
        print('Prop Pitch: %.3f In' % (AC.propulsion.pitch))
        print('Thrust Curve: ' + ','.join("%f" % n for n in AC.propulsion.thrustCurve))
        print('RPM: %.3f' % (AC.propulsion.motorKV* (AC.propulsion.cellNum * 3.7)))

        # Set output to updated instance of aircraft
        unknowns['out_aircraft'] = AC
