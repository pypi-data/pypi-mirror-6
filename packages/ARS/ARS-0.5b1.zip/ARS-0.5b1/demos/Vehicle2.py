"""Runs a simulation of a vehicle with two powered wheels and one
free-rotating spherical wheel.

"""
from ars.app import Program
import ars.constants as cts


class Vehicle2(Program):

	TORQUE = 30
	OFFSET = (3, 1, 3)
	FLOOR_BOX_SIZE = (20, 0.01, 20)

	def __init__(self):
		"""Constructor, calls the superclass constructor first."""
		Program.__init__(self)
		self.key_press_functions.add('up', self.go_forwards, True)
		self.key_press_functions.add('down', self.go_backwards, True)
		self.key_press_functions.add('left', self.turn_left, True)
		self.key_press_functions.add('right', self.turn_right, True)

	def create_sim_objects(self):
		"""Implementation of the required method.

		Creates and sets up all the objects of the simulation.

		"""
		offset = self.OFFSET

		# (length, radius, center, density)
		wheelR = self.sim.add_cylinder(0.4, 0.3, (0, 0, -0.5), density=1)
		wheelL = self.sim.add_cylinder(0.4, 0.3, (0, 0, 0.5), density=1)
		# (radius, center, density)
		ball = self.sim.add_sphere(0.3, (1, 0, 0), density=1)
		# (size, center, density)
		chassis = self.sim.add_box((2, 0.2, 1.5), (0.5, 0.45, 0), density=10)

		self.sim.add_rotary_joint(
			'r1',                          # name
			self.sim.get_object(chassis),  # obj1
			self.sim.get_object(wheelR),   # obj2
			None,                          # anchor
			cts.Z_AXIS)                    # axis

		self.sim.add_rotary_joint(
			'r2',
			self.sim.get_object(chassis),
			self.sim.get_object(wheelL),
			None,
			cts.Z_AXIS)

		self.sim.add_ball_socket_joint(
			'bs',                          # name
			self.sim.get_object(chassis),  # obj1
			self.sim.get_object(ball),     # obj2
			None)                          # anchor

		self.sim.get_object(wheelR).offset_by_position(offset)
		self.sim.get_object(wheelL).offset_by_position(offset)
		self.sim.get_object(ball).offset_by_position(offset)
		self.sim.get_object(chassis).offset_by_position(offset)

		# test
		# try:
		# 	self.sim.get_object(wheelR).actor.set_color((0.8, 0, 0))
		# except AttributeError:
		# 	# if visualization is deactivated, there is no actor
		# 	pass

	def go_forwards(self):
		"""Rotate both powered wheels in the same direction, forwards."""
		self.sim.get_joint('r1').add_torque(self.TORQUE)
		self.sim.get_joint('r2').add_torque(self.TORQUE)

	def go_backwards(self):
		"""Rotate both powered wheels in the same direction, backwards."""
		self.sim.get_joint('r1').add_torque(-self.TORQUE)
		self.sim.get_joint('r2').add_torque(-self.TORQUE)

	def turn_left(self):
		"""Rotate vehicle counter-clockwise (from above)."""
		self.sim.get_joint('r1').add_torque(-self.TORQUE)
		self.sim.get_joint('r2').add_torque(self.TORQUE)

	def turn_right(self):
		"""Rotate vehicle clockwise (from above)."""
		self.sim.get_joint('r1').add_torque(self.TORQUE)
		self.sim.get_joint('r2').add_torque(-self.TORQUE)
