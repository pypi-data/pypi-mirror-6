# For testing purposes we might need to set mpl backend before any
# other import of matplotlib.
def _set_mpl_backend():
    import os
    import matplotlib as mpl

    env_backend = os.environ.get('MATPLOTLIB_BACKEND')
    if env_backend:
        # we were instructed
        mpl.use(env_backend)

_set_mpl_backend()

# This is the only place the version is specified and 
# used in both setup.py and docs/conf.py to set the 
# version of ggplot.
__version__ = '0.4.5'

from .ggplot import *
from .components import aes
from .geoms import *
from .scales import *
from .themes import *
from .utils import *
from .exampledata import *
