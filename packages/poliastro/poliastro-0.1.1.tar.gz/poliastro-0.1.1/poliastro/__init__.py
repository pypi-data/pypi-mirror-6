"""
=========
poliastro
=========

Utilities and Python wrappers for Orbital Mechanics

"""

__version__ = '0.1.1'

from . import angles
from . import iod
from . import twobody
from .logging import logger

from numpy.testing import Tester
test = Tester().test
bench = Tester().bench
