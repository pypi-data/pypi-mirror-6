=======================
thermocouples_reference
=======================

Python module containing calibration data and lookup functions for standard
`thermocouples`_ of types **B**, **C**, **D**, **E**, **G**, **J**, **K**,
**N**, **R**, **S**, **T**.

Usage and examples
------------------

Below, the first computation shows that the type K termocouple
`emf reference function`_ at 42 °C is 1.694 mV (`compare to NIST table`_);
the second calculation shows how passing in an array applies the function
for each element, in the style of numpy:

  >>> from thermocouples_reference import thermocouples
  >>> typeK = thermocouples['K']
  >>> typeK
  Type K (chromel :: alumel) thermocouple reference (-270.0 to 1372.0 Celsius)
  >>> typeK.emf_mVC(42)
  1.6938477049901346
  >>> typeK.emf_mVC([-3.14159, 42, 54])
  array([-0.12369326,  1.6938477 ,  2.18822176])

The function is called ``emf_mVC`` just to remind you that its output is
always millivolts and its input is always degrees Celsius. For SI-minded
folks a function ``emf_VK`` is also provided, however note that its output
is still zeroed at 273.15 K.

An inverse lookup function is provided that you can use to get a temperature
out of a measured voltage, including cold junction compensation effects.
If we put our type K thermocouple into a piece of spam and we read 1.0 mV,
using our voltmeter at room temperature (23 °C), then the spam is at
47 °C. [1]_

  >>> typeK.inverse_CmV(1.0, Tref=23.0)
  47.48175880786998
  >>> typeK.emf_mVC(47.48175880786998) - typeK.emf_mVC(23) # confirm
  1.0

You can also compute derivatives of the emf function (these are functional
derivatives, not finite differences). The Seebeck coefficients of chromel
and alumel differ by 42.00 μV/K, at 687 °C:

  >>> typeK.emf_mVC(687,derivative=1)
  0.041998175982382979

Data sources
------------

Graphs of functions (if you don't see anything, see
`low temperature types here`_ and
`high temperature types here`_):

.. image:: https://upload.wikimedia.org/wikipedia/commons/f/f8/Low_temperature_thermocouples_reference_functions.svg
.. image:: https://upload.wikimedia.org/wikipedia/commons/c/c3/High_temperature_thermocouples_reference_functions.svg

Readers may be familiar with thermocouple lookup tables (`example table`_).
Such tables are computed from standard reference functions, generally
piecewise polynomials. [2]_ This module contains the source polynomials
*directly*, and so in principle it is more accurate than any lookup table.

- Types B,E,J,K,N,R,S,T use coefficients from `NIST`_, and are calibrations
  to the `ITS-90`_ scale. The ITS-90 scale is believed to track the true
  thermodynamic temperature very closely. [3]_
- Types C,D,G use coefficients found from a publication of OMEGA Engineering
  Inc., and are calibrations to `IPTS-68`_ or ITS-90 scale, not sure which
  (the difference is negligible since these thermocouples have larger
  manufacturing variations).

The NIST tables also include approximate inverse polynomials for temperature
lookup based on a given compensated emf value. Those inverse polynomials are
*not included* in this module.

Requirements
------------

- ``numpy``
- ``scipy`` (optional, only needed for inverse lookup)
- ``python2`` or ``python3`` languages

Installation
------------

Recommended installation is via pip. First, `install pip`_. Then::

    pip install thermocouples_reference --user

(Remove the ``--user`` option if you are superuser and want to install
system-wide.)

Disclaimer
----------
This module is provided for educational purposes. For any real-world
process, I strongly recommend that you check the output of this module
against a known good standard.

I make no warranties as to the accuracy of this module, and shall
not be liable for any damage that may result from errors or omissions.

.. _thermocouples: https://en.wikipedia.org/wiki/Thermocouple
.. _emf reference function: https://en.wikipedia.org/wiki/Thermocouple#Thermocouple_characteristic_function
.. _install pip: http://www.pip-installer.org/en/latest/installing.html
.. _compare to NIST table: http://srdata.nist.gov/its90/download/type_k.tab
.. _low temperature types here: https://commons.wikimedia.org/wiki/File:Low_temperature_thermocouples_reference_functions.svg
.. _high temperature types here: https://commons.wikimedia.org/wiki/File:High_temperature_thermocouples_reference_functions.svg
.. _NIST: http://srdata.nist.gov/its90/main/
.. _example table: http://srdata.nist.gov/its90/download/type_k.tab
.. _ITS-90: https://en.wikipedia.org/wiki/International_Temperature_Scale_of_1990
.. _IPTS-68: http://www.bipm.org/en/si/history-si/temp_scales/ipts-68.html
.. [1] This is the optimal temperature for spam. Always make sure your
       spam reads around 1 millivolt and you'll have a tasty treat.
.. [2] A notable exception is NIST's type K curve which uses a polynomial plus
       gaussian. The gaussian conveniently captures a wiggle in the Seebeck
       coefficient of alumel, that happens around 130 °C.
.. [3] The error *T* − *T*\ :sub:`90` is quite small, of order 0.01 K for
       everyday conditions (up to about 200 °C), rising to around 0.05 K up
       at 1000 °C, and increasing even further after that. See
       `Supplementary Information for the ITS-90`_. Generally your
       thermocouple accuracy will be more limited by manufacturing variations
       and by degradation of the metals in the thermal gradient region.
.. _Supplementary Information for the ITS-90: http://www.bipm.org/en/publications/mep_kelvin/its-90_supplementary.html