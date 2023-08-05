#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'yarnaid'

import properties
from ext.angles import Zone, Angle
from pixelmap import gPixelMap as PixelMap
from pointsource import PointSource
from tools import convertion as convert
from tools import colorer
from tools.logger import logger
import tools.tools
import os
from cl import Cl


mappat_path = os.path.join(tools.tools.glesp_exec, tools.tools.glesp['mappat'])
if not os.path.exists(mappat_path):
    raise ImportError('Cannot import module {}. No mappat binary found in {}'.format(
        __name__, tools.tools.glesp_exec
    ))