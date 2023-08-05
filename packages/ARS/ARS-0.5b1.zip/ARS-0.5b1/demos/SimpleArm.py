"""Runs a simulation of a simple arm, with 2 links and 2 rotary joints.

"""
from ars.app import Program
import ars.utils.mathematical as mut
import ars.constants as cts


class SimpleArm(Program):

	TORQUE = 3
	OFFSET = (2.5, 1, 2.5)

	# ((size, center), density)
	BOX_PARAMS = (((3, 0.5, 3), (0, -0.75, 0)), {'density': 1})
	# ((length, radius, center), density)
	LINK1_PARAMS = ((0.8, 0.1, (0, 0, 0)), {'density': 1})
	LINK2_PARAMS = ((0.6, 0.1, (0, 0.7, 0.2)), {'density': 1})

	def __init__(self):
		Program.__init__(self)
		self.key_press_functions.add('a', self.rotate_clockwise)
		self.key_press_functions.add('z', self.rotate_counterlockwise)

	def create_sim_objects(self):

		box = self.sim.add_box(*self.BOX_PARAMS[0], **self.BOX_PARAMS[1])
		link1 = self.sim.add_capsule(
			*self.LINK1_PARAMS[0], **self.LINK1_PARAMS[1])
		link2 = self.sim.add_capsule(
			*self.LINK2_PARAMS[0], **self.LINK2_PARAMS[1])

		# bodies are rotated before attaching themselves through joints
		self.sim.get_object(link1).rotate(cts.X_AXIS, mut.pi / 2)
		self.sim.get_object(link2).rotate(cts.X_AXIS, mut.pi / 2)

		self.sim.get_object(box).offset_by_position(self.OFFSET)
		self.sim.get_object(link1).offset_by_position(self.OFFSET)
		self.sim.get_object(link2).offset_by_position(self.OFFSET)

		self.sim.add_rotary_joint(
			'r1',                        # name
			self.sim.get_object(box),    # obj1
			self.sim.get_object(link1),  # obj2
			None,                        # anchor
			cts.Y_AXIS)                  # axis

		r2_anchor = mut.sub3(
			self.sim.get_object(link2).get_position(),
			(0, self.LINK2_PARAMS[0][0] / 2, 0))  # (0, length/2, 0)
		self.sim.add_rotary_joint(
			'r2',
			self.sim.get_object(link1),
			self.sim.get_object(link2),
			r2_anchor,
			cts.Z_AXIS)

	def rotate_clockwise(self):
		self.sim.get_joint('r1').add_torque(self.TORQUE)

	def rotate_counterlockwise(self):
		self.sim.get_joint('r1').add_torque(-self.TORQUE)
