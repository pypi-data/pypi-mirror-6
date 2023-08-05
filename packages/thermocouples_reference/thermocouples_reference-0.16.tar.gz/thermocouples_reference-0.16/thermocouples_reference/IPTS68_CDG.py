"""    
    This module uses thermocouple reference functions for types C,D,G.

    You can access the lookup table objects like so:
        typeC = <this module>.thermocouples['C']

    Nitpicky note on calibration:
        It is not totally clear whether these are IPTS68 or ITS90 scales.
        The difference between IPTS68 and ITS90 scales is at worst
        0.4 deg C over the range 0 to 1400 deg C;
        At 1500 deg C, IPTS68 reads 0.44 deg C higher
        At 2000 deg C, IPTS68 reads 0.72 deg C higher
        At 2500 deg C, IPTS68 reads 1.07 deg C higher
        (see http://www.its-90.com/its-90p4.html, Table 6)
        Anyway at the manufacturing variations in WRe thermocouples
        is somewhere around +/-4 to +/-20 deg C.

    Disclaimers:
    (Author) I make no warranties as to the accuracy of this module, and shall
           not be liable for any damage that may result from errors or omissions.

    (Note: This module is generated code from create_tables_CDG.py.)
"""

__copyright__ = "public domain"

import numpy as np
from .function_types import Thermocouple_Polynomial_Function

_note = 'IPTS68 or ITS90 reference function'
_tclist = []

# The coefficients of this polynomial have been converted from
# a Fahrenheit polynomial with 7 significant figures, and have
# been stored here with longer precision to avoid further inaccuracy.
_tclist.append(Thermocouple_Polynomial_Function('G', _note,
    [[0.,2320.,
np.array([ -2.2222283359680003e-16,   2.2112702944358399e-12,
        -1.0316119658501839e-08,   2.1425207201941232e-05,
         1.2905824431600024e-03,   0.0000000000000000e+00]),
    None]], composition='W :: W-26%Re'))

# The coefficients of this polynomial have been converted from
# a Fahrenheit polynomial with 7 significant figures, and have
# been stored here with longer precision to avoid further inaccuracy.
_tclist.append(Thermocouple_Polynomial_Function('C', _note,
    [[0.,2320.,
np.array([ -4.9446064258560002e-16,   3.6006582486412798e-12,
        -1.0489145155399067e-08,   1.2252598548103214e-05,
         1.3387722982319094e-02,   0.0000000000000000e+00]),
    None]], composition='W-5%Re :: W-26%Re'))

_tclist.append(Thermocouple_Polynomial_Function('D', _note,
    [[0.,783., np.array([
        -1.4240735e-15,
         7.9498033e-12,
        -1.8464573e-8,
         2.0592621e-5,
         9.5685256e-3,
         0.,
    ]), None],
    [783.,2320., np.array([
        -7.9026726e-16,
         5.3743821e-12,
        -1.4935266e-8,
         1.8666488e-5,
         9.9109462e-3,
         0.,
    ]), None] ], composition='W-3%Re :: W-25%Re'))

thermocouples = {tc.type : tc for tc in _tclist}
del _tclist

#end of module

