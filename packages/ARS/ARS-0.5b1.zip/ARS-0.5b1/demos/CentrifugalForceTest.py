"""Demo of a test of ODE's and ARS's capability of simulating correctly a
system where inertia and centrifugal force intervene. The theoretical angle
(theta) of the cable that
holds the ball can be obtained with this equation:

	tan(theta) / (d + l*sin(theta)) = omega^2 / g
		d: distance from pole to anchor
		l: "cable" length
		omega: angular velocity of pole and ball
		g: gravity

However, theta must be calculated with a numerical solver since no simple
analytical solution exists.

"""
from ars.app import Program, dispatcher, logger
import ars.utils.mathematical as mut
import ars.constants as cts
from ars.model.simulator import signals

#View point
#==============================================================================
# vp_hpr = (90.0, 0.0, 0.0) # orientation [degrees]
#
# QUICKSTEP_ITERS = 20 # # of iterations for the QuickStep function
#
# GRAVITY = -9.81
# GLOBAL_CFM = 1e-10 # default for ODE with double precision
# GLOBAL_ERP = 0.8
#==============================================================================


def get_sphere_volume(radius):
	return 4.0 / 3.0 * mut.pi * (radius ** 3)


class CentrifugalForceTest(Program):

	OFFSET = (2, 0.5, 2)
	# ((size, center), density)
	BOX_PARAMS = (((5, 0.5, 5), (0, -0.25, 0)), {'density': 1})

	WINDOW_SIZE = (900, 600)
	CAMERA_POSITION = (2, 5, 10)  # position [meters]
	FPS = 50
	STEPS_PER_FRAME = 20  # 200 #STEP_SIZE = 1e-5 # 0.01 ms

	POLE_SPEED_STEP = 0.01
	POLE_VISUAL_RADIUS = 0.05  # 5 cm. how it will be displayed
	POLE_HEIGHT = 2  # [meters]
	POLE_INITIAL_POS = (0.0, 1.0, 0.0)

	BALL_MASS = 1.0  # [kg]
	BALL_RADIUS = 0.01  # [cm]
	BALL_VISUAL_RADIUS = 0.1  # [cm]
	BALL_INITIAL_POS = (0.0, 1.0, 1.0)

	JOINT1_ANCHOR = (0.0, 0.0, 0.0)
	JOINT1_AXIS = (0.0, 1.0, 0.0)  # Y-axis
	JOINT1_FMAX = 100
	JOINT2_ANCHOR = (0.0, 2.0, 1.0)
	JOINT2_AXIS = (1.0, 0.0, 0.0)  # X-axis

	CABLE_LENGTH = mut.length3(mut.sub3(BALL_INITIAL_POS, JOINT2_ANCHOR))

	JOINT2_ANGLE_RATE_CONTROLLER_KP = 500.0
	JOINT1_ANGLE_RATE_INITIAL = 3.0

	def __init__(self):
		Program.__init__(self)
		self.key_press_functions.add('a', self.inc_joint1_vel)
		self.key_press_functions.add('z', self.dec_joint1_vel)
		#self.key_press_functions.add('f', self.rotate_clockwise)

		dispatcher.connect(self.on_pre_frame, signals.SIM_PRE_FRAME)

		self.joint1_vel_user = self.JOINT1_ANGLE_RATE_INITIAL
		self.large_speed_steps = True
		#TODO: set ERP, CFM

	def create_sim_objects(self):
		box = self.sim.add_box(*self.BOX_PARAMS[0], **self.BOX_PARAMS[1])
		# It doesn't really matter if pole has mass since speed is set
		pole = self.sim.add_cylinder(
			self.POLE_HEIGHT,
			self.POLE_VISUAL_RADIUS,
			self.POLE_INITIAL_POS,
			density=1.0)

		ball_density = self.BALL_MASS / get_sphere_volume(self.BALL_RADIUS)
		# FIXME: visual radius => did not affect the results noticeably
		ball = self.sim.add_sphere(
			self.BALL_RADIUS,
			self.BALL_INITIAL_POS,
			density=ball_density)

		# bodies are rotated before attaching themselves through joints
		self.sim.get_object(pole).rotate(cts.X_AXIS, mut.pi / 2)

		self.sim.get_object(box).offset_by_position(self.OFFSET)
		self.sim.get_object(pole).offset_by_position(self.OFFSET)
		self.sim.get_object(ball).offset_by_position(self.OFFSET)

		self.sim.add_rotary_joint(
			'r1',                       # name
			self.sim.get_object(box),   # obj1
			self.sim.get_object(pole),  # obj2
			None,                       # anchor
			self.JOINT1_AXIS)           # axis

		self.sim.add_rotary_joint(
			'r2',
			self.sim.get_object(pole),
			self.sim.get_object(ball),
			mut.add3(self.OFFSET, self.JOINT2_ANCHOR),
			self.JOINT2_AXIS)

		self.box = box
		self.pole = pole
		self.ball = ball

	def on_pre_frame(self):
		try:
			self.set_joint1_speed()
			self.apply_friction()

			ball_pos = self.sim.get_object(self.ball).get_position()
			ball_vel = self.sim.get_object(self.ball).get_linear_velocity()
			ball_omega = self.sim.get_object(self.ball).get_angular_velocity()
			z_top = self.JOINT2_ANCHOR[1]
			theta_sim = mut.acos(
				(z_top - ball_pos[1] + self.OFFSET[1]) / self.CABLE_LENGTH)

			print((ball_pos, ball_vel, ball_omega, theta_sim))

		except Exception:
			logger.exception("Exception when executing on_pre_frame")

	def inc_joint1_vel(self):
		self.joint1_vel_user += self.POLE_SPEED_STEP

	def dec_joint1_vel(self):
		self.joint1_vel_user -= self.POLE_SPEED_STEP

	def set_joint1_speed(self):
		self.sim.get_joint('r1').joint.set_speed(self.joint1_vel_user, self.JOINT1_FMAX)

	def apply_friction(self):
		torque = -self.JOINT2_ANGLE_RATE_CONTROLLER_KP * self.sim.get_joint('r2').joint.angle_rate
		self.sim.get_joint('r2').joint.add_torque(torque)
