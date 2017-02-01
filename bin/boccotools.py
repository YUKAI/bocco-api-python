# encoding: utf-8
from __future__ import absolute_import
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(ROOT)

import bocco

bocco.cli.cli(obj={})
