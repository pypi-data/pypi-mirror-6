"""ARS is a physically-accurate robotics simulator written in Python.
It's main purpose is to help researchers to develop mobile
manipulators and, in general, any multi-body system.
It is open-source, modular, easy to learn and use,
and can be a valuable tool in the process of robot design,
in the development of control and reasoning algorithms,
as well as in teaching and educational activities.

"""
# based on: ``django.__init__`` @ commit 5b644a5
# see its license in docs/Django BSD-LICENSE.txt

# for a "real" release, replace 'alpha' with 'final'
VERSION = (0, 5, 0, 'beta', 1)  # i.e. 0.5b1


def get_version(*args, **kwargs):
	# Only import if it's actually called.
	from .utils.version import get_version
	return get_version(*args, **kwargs)
