"""
PyFeyn - a simple Python interface for making Feynman diagrams.
"""

__author__ = "Andy Buckley & Georg von Hippel (pyfeyn at projects.hepforge.org)"
__version__ = "0.3.4"
__date__ = "$Date: 2014-02-25 11:14:01 +0100 (Tue, 25 Feb 2014) $"
__copyright__ = "Copyright (c) 2007-2014 Andy Buckley and Georg von Hippel"
__license__ = "GPL"

## Set __all__ (for "from pyfeyn import *")
__all__ = ["diagrams", "points", "blobs", "lines", "deco", "utils", "config"]

## Import PyX and set up some things
try:
    import pyx
except:
    print "You don't have PyX - that's a problem unless you're just running the setup script."
    import sys
    sys.exit()

## Check the version
from distutils.version import StrictVersion as Version
pyxversion = Version(pyx.version.version)
if pyxversion < Version("0.9.0"):
    print "Warning: PyFeyn may not work with PyX versions older than 0.9!"

## Units
pyx.unit.set(uscale = 4, vscale = 4, wscale = 4, xscale = 4)
pyx.unit.set(defaultunit = "cm")

## TeX stuff
pyx.text.defaulttexrunner.set(mode="latex")
import subprocess
try:
  subprocess.check_output(["kpsewhich","hepnicenames.sty"])
  pyx.text.defaulttexrunner.preamble(r"\usepackage{hepnicenames}")
except:
  print "Warning: hepnicenames package not found!"

