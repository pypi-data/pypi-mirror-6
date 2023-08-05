"""
Python module containing calibration data and lookup functions for standard
thermocouples of types B, C, D, E, G, J, K, N, R, S, T.

You can access the lookup table objects like so::

    import thermocouples_reference
    typeK = thermocouples_reference.thermocouples['K']

Find the latest version at https://pypi.python.org/pypi/thermocouples_reference

===DISCLAIMER===

This module is provided for educational purposes. For any real-world
process, I strongly recommend that you check the output of this module
against a known good standard.

I make no warranties as to the accuracy of this module, and shall
not be liable for any damage that may result from errors or omissions.

================

"""

__author__    = "User:Nanite @ wikipedia"
__copyright__ = "public domain"
__version__   = "0.16"

from .IPTS68_CDG import thermocouples as thermocouples_IPTS68_CDG
from .ITS90_nist import thermocouples as thermocouples_ITS90_nist
from .function_types import Thermocouple_Polynomial_Function

# assemble thermocouples list, give preference to ITS90 NIST
thermocouples = dict()
thermocouples.update(thermocouples_IPTS68_CDG)
thermocouples.update(thermocouples_ITS90_nist)

