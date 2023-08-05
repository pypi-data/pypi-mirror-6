# -*- python -*-
#
#  Copyright 2013
#
#  File author(s): Thomas Cokelaer <cokelaer@gmail.com>
#
"""Common tools to get the correct filename and pathname. """
__version__ = "$Rev: 32 $"
import pkg_resources
try:
    version = pkg_resources.require("easydev")[0].version
except:
    version = __version__

import copybutton
from copybutton import *

import doc
from doc import *

import logging_tools
from logging_tools import *

import sphinx_themes
from sphinx_themes import *

import tools
from tools import *

import multisetup

import paths
from paths import *

import package
from package import *

import config_tools
from config_tools import *

import url
from url import *

#import dependencies
from dependencies import get_dependencies
