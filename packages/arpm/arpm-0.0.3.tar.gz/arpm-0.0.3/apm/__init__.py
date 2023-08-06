__version__ = '0.0.3'
__author__ = "Dalton Hubble"
__email__ = "dghubble@gmail.com"
cmdname = "arpm"

import sys
from core import RoleRepository
from exceptions import APMException

# role repository setup must succeed
try:
    repository = RoleRepository()
except APMException as e:
    sys.exit(e)