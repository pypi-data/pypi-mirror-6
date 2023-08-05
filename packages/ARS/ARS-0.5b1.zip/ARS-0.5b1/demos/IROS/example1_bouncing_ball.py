"""Example #1. To achieve the same results reported in the paper, the contact
joint bounce parameter (in :func:`ars.model.simulator.collision near_callback`)
must be set to 0.9, instead of the default 0.2 value.

"""
from ars.app import Program, dispatcher, logger
from ars.model.simulator import signals


class Example1(Program):

	FPS = 50
	STEPS_PER_FRAME = 80

	HEIGHT = 1
	RADIUS = 0.01
	CENTER = (1, HEIGHT + RADIUS, 1)
	MASS = 1

	def __init__(self):
		Program.__init__(self)
		dispatcher.connect(self.on_pre_step, signals.SIM_PRE_STEP)

	def create_sim_objects(self):
		self.sphere = self.sim.add_sphere(
			self.RADIUS, self.CENTER, mass=self.MASS)

	def on_pre_step(self):
		try:
			time = self.sim.sim_time
			sim_ball = self.sim.get_object(self.sphere)
			pos = sim_ball.get_position()
			vel = sim_ball.get_linear_velocity()

			#print('time: %f, pos: %f, vel: %f' % (time, pos[1], vel[1]))
			print('%.7e\t%.7e\t%.7e' % (time, pos[1], vel[1]))

		except Exception:
			logger.exception("Exception when executing on_pre_step")
