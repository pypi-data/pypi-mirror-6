# qmpy/__init__.py

"""
qmpy is a package containing many tools for computational materials science. 
"""
import logging
import logging.handlers
import os
from os.path import dirname, abspath
import sys
import re

INSTALL_PATH = abspath(dirname(__file__))
LOG_PATH = INSTALL_PATH+'/logs/'

if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# the default log level for normal loggers
logLevel = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(logLevel)

FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
FORMAT_SHORT = '%(levelname)-8s %(message)s'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(FORMAT, TIME_FORMAT)
short_formatter = logging.Formatter(FORMAT_SHORT)
console = logging.StreamHandler()
console.setFormatter(short_formatter)

# uncomment to set debugging output for all normal loggers
#console.setLevel(logging.DEBUG)

general = logging.handlers.WatchedFileHandler(LOG_PATH+'qmpy.log')
general.setFormatter(formatter)

logger.addHandler(general)
logger.addHandler(console)

class qmpyBaseError(Exception):
    """Baseclass for qmpy Exceptions"""

try:
    import ase
    FOUND_ASE = True
except ImportError:
    FOUND_ASE = False
    logging.warn('Failed to import ASE')

try:
    import pulp
    FOUND_PULP = True
except ImportError:
    FOUND_PULP = False
    logging.warn('Failed to import PuLP')

try:
    import matplotlib
    FOUND_MPL = True
except ImportError:
    FOUND_MPL = False
    logging.warn('Failed to import matplotlib')

try:
    import pyspglib 
    FOUND_SPGLIB = True
except ImportError:
    FOUND_SPGLIB = False

### Kludge to get the django settings module into the path
sys.path.insert(-1, INSTALL_PATH)
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'qmpy.db.settings'

from models import *
from analysis import *
from analysis.thermodynamics import *
from analysis.symmetry import *
from analysis.vasp import *
from computing import *

