#python stantdard libraries 
from __future__ import print_function
from time import localtime, strftime, time

# addition python libraries 
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

#open MDAO libraries
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver

#user defined libraries
from PostProcess import post_process
from weight import weight
from obj import obj
from lib_plot import *


FFMpegWriter = animation.writers['ffmpeg']
metadata = dict(title='MACH MDO', artist='MACH',comment='MDO Animation') 
writer = FFMpegWriter(fps=15, metadata=metadata)

class Constrained_MDO(Group):

	def __init__(self):
		super(Constrained_MDO,self).__init__()


		# ====================================== Params =============================================== #

		self.add('b_wing',IndepVarComp('b_wing',2.5)) 							# Wingspan (feet) 
		self.add('dihedral',IndepVarComp('dihedral',1.0))						# Wing dihedral angle (degrees)
		self.add('sweep',IndepVarComp('sweep', np.array([0.0, 0.0, 0.0, 10.0])))# Quarter Chord Sweep in degrees (cubic)
		self.add('chord',IndepVarComp('chord',np.array([-0.3, -2, -0.5, 3])))	# Chord (cubic constants: chord = ax^3+bx^2+c*x+d, x = half-span position)		# Taper ratio at 3 
		self.add('dist_LG',IndepVarComp('dist_LG', 1.0))						# Distance between CG and landing gear (feet)
		self.add('boom_len',IndepVarComp('boom_len', 4.0))						# Length of tailboom (feet)
		self.add('camber',IndepVarComp('camber',np.array([1.0 , 1.0, 1.0,1.0])))# Wing camber (cubic constants: camber = c_ax^3+c_bx^2+c_c*x + c_d, x = half-span position)
		self.add('max_camber',IndepVarComp('max_camber',np.array([1.0 , 1.0, 1.0,1.0])))		# Horizontail Tail Span 
		self.add('thickness',IndepVarComp('thickness',np.array([1.0 , 1.0, 1.0,1.0])))		# Tail Root airfoil Cord 
		self.add('max_thickness',IndepVarComp('max_thickness',np.array([1.0 , 1.0, 1.0,1.0])))	# Vertical Tail Span
		self.add('Ainc',IndepVarComp('Ainc',np.array([1.0 , 1.0, 1.0,1.0])))	# Boom Length
		self.add('c_r_ht',IndepVarComp('c_r_ht',np.array([0.0 , 0.0, 0.0,1.0])))
		self.add('c_r_vt',IndepVarComp('c_r_vt',np.array([0.0 , 0.0, 0.0,1.0])))
		self.add('b_htail',IndepVarComp('b_htail',3.0))
		self.add('b_vtail',IndepVarComp('b_vtail',1.0))
		
  
# ====================================== Connections ============================================ # 


		
# ==================================== Initailize plots for animation ===================================== #


# ============================================== Create Problem ============================================ #
prob = Problem()
prob.root = Constrained_MDO()

# ================================================ Add Driver ============================================== #
prob.driver = pyOptSparseDriver()
prob.driver.options['optimizer'] = 'ALPSO'
prob.driver.opt_settings = {'SwarmSize': 40, 'maxOuterIter': 30,\
				'maxInnerIter': 7, 'minInnerIter' : 7,  'seed': 2.0}

# prob.driver = ScipyOptimizer()
# prob.driver.options['optimizer'] = 'SLSQP'
# prob.root.fd_options['force_fd'] = True	
# prob.root.fd_options['form'] = 'forward'
# prob.root.fd_options['step_size'] = 1e-3,


# ===================================== Add design Varibles and Bounds ==================================== #
prob.driver.add_desvar('b_wing.b_wing',   				lower = 1,    upper = 3 )
prob.driver.add_desvar('dihedral.dihedral',   			lower = 1,    upper = 3 )
prob.driver.add_desvar('sweep.sweep',   				lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
prob.driver.add_desvar('chord.chord',        			lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
prob.driver.add_desvar('t2.t2',           				lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('t3.t3', 		  				lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('t4.t4',			  				lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('t5.t5',			  				lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('dist_LG.dist_LG', 				lower = 0.05, upper = 0.1)
prob.driver.add_desvar('boom_len.boom_len', 			lower = 0.5,  upper = 1.5)
prob.driver.add_desvar('camber.camber',         		lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
										        		upper = np.array([0.15, 0.14, 0.14, 0.14, 0.14 ]))
prob.driver.add_desvar('max_camber.max_camber', 		lower = np.array([0.35, 0.35, 0.35, 0.35, 0.35 ]),\
														upper = np.array([0.50, 0.50, 0.50, 0.50, 0.50 ]))
prob.driver.add_desvar('thickness.thickness',   		lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
											    		upper = np.array([0.15, 0.15, 0.15, 0.15, 0.15 ]) )
prob.driver.add_desvar('max_thickness.max_thickness', 	lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
prob.driver.add_desvar('Ainc.Ainc', 	  				lower = 0.15, upper = 0.3)
prob.driver.add_desvar('c_r_ht.c_r_ht', 	  			lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
prob.driver.add_desvar('c_r_vt.c_r_vt', 	  			lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
													  	upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )
prob.driver.add_desvar('b_htail.b_htail', 				lower = 0.6,  upper = 1.2)
prob.driver.add_desvar('b_vtail.b_vtail', 				lower = 0.6,  upper = 1.2)
# add objective
prob.driver.add_objective('obj.score')



# =============== Setup & Run ================ #
prob.setup()

with writer.saving(fig, "OPT_#.mp4", 100):
	prob.run()


# ======================================== Post-Processing ============================================== #

print('================  Final Results ===================')
print('\n')
print('Score: ' + str(-1*prob['obj.score']))


