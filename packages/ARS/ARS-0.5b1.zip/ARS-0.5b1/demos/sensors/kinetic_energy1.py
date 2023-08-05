"""Shows usage of the KineticEnergy sensor, with the FallingBalls program.
Sensor data is stored in a queue, which is retrieved after the simulation ends
(but it can be accessed at any time).

Sensor is created in the `create_sim_objects` method.
	'self.sensor = sensors.KineticEnergy(ball_object)'
It is updated in the `on_post_step` method
	'self.sensor.on_change(time)'
Sensor measurements can be retrieved at any time
	'self.sensor.data_queue.pull()'

"""
from ars.app import dispatcher
from ars.model.robot import sensors
from ars.model.simulator import signals

from .base import FallingBalls, PrintDataMixin, logger


class KineticEnergy(FallingBalls, PrintDataMixin):

	def __init__(self):
		FallingBalls.__init__(self)
		dispatcher.connect(self.on_post_step, signals.SIM_POST_STEP)

	def create_sim_objects(self):
		FallingBalls.create_sim_objects(self)
		ball_object = self.sim.get_object(self.ball1)
		self.sensor = sensors.KineticEnergy(ball_object)

	def on_post_step(self):
		try:
			time = self.sim.sim_time
			self.sensor.on_change(time)
		except Exception:
			logger.exception("Exception when executing on_post_step")
