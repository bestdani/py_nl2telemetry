# For the case that nl2telemetry has not been added to PYTHONPATH
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).absolute().parent.parent))

"""
Launch NoLimits 2 with the "--telemetry" option, then execute.
"""

from pprint import pprint

from nl2telemetry import NoLimits2
from nl2telemetry.message import get_telemetry, Answer

with NoLimits2() as nl2:
    nl2.send(get_telemetry)
    data = Answer.get_data(nl2.receive())
    pprint(data.__dict__)
