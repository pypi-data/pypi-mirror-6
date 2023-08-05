# -*- coding: shiftjis -*-
import os, sys
from setuptools import setup, find_packages, Extension

あいうえお
if sys.version_info[:2] < (3, 3):
    raise RuntimeError('Kaa requires Python 3.3 or later.')

