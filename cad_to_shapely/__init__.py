
# For relative imports to work in Python 3.6
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))


import utils
import cadimporter
import svg
import dxf

try:
    import examples
except ImportError:
    pass



