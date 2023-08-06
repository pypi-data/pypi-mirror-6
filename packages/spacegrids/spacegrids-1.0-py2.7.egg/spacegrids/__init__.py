""" 
"""
import numpy as np
import numpy.ma as ma
import matplotlib as mpl
import matplotlib.pyplot as plt
import types
import inspect

import glob
  
try:
  import Scientific.IO.NetCDF
  from Scientific.IO import NetCDF
  from Scientific.IO.NetCDF import *
  no_cdf =0
except:
  no_cdf = 1
  
import inspect 
  
from scipy.interpolate import griddata

import fnmatch
import os
import copy

import itertools

if no_cdf == 1:
  print "NetCDF library not found."

