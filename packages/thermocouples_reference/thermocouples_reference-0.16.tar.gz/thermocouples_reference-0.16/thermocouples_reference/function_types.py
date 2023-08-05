"""
    Python module for computing thermocouple emf values from temperatures.
    This module just contains the generic thermocouple object and helper
    functions.
"""

__author__    = "User:Nanite @ wikipedia"
__copyright__ = "public domain"

import numpy as np
_op = None

class Thermocouple_Polynomial_Function(object):
    """ Thermocouple lookup object using polynomials (+ optional gaussian).

        Main methods:
            .emf_mVC(T)
            .emf_VK(T)
            .inverse_CmV(mV)

        To look up an emf reference function value, just call
            tc.emf_mVC(42)
            --> 1.69384770499      (this is the K-type function in mV, at 42 deg C)
        or you can input arrays for speed
            tc.emf_mVC([-3.14159,42,54])
            --> array([-0.12369326,  1.6938477 ,  2.18822176])

        Advice on usage of thermocouple references:
          Never compute     tc.emf_mVC(Thot - Tcold) <--- this is never correct!
          Instead you want  tc.emf_mVC(Thot) - tc.emf_mVC(Tcold)
    """
    def __init__(self,ttype,family,table,composition=''):
        # internally used constructor
        # look at existing objects to understand the table structure
        # note: table entries must be listed in ascending order of ranges,
        #       and must use degrees Celsius and millivolt units.
        self.type        = ttype
        self.family      = family
        self.table       = table
        self.composition = composition

    def get_tempmin(self):
        return self.table[0][0]
    def get_tempmax(self):
        return self.table[-1][1]

    def __repr__(self):
        r = "{:.1f} to {:.1f}".format(self.get_tempmin(),self.get_tempmax())
        if self.composition:
            cmpstr = " ("+self.composition+")"
        else:
            cmpstr = ''
        return "Type "+self.type+cmpstr+" thermocouple reference ("+r+" Celsius)"
 
    def emf_mVC(self,T,derivative=0,out_of_range="raise"):
        """ Takes temperatures and returns emf voltages.

            T : array_like
                Temperature or array of temperatures, in degrees Celsius
            derivative: integer
                Use this parameter to evaluate the functional derivative of the emf
                function at a given temperature. Default is derivative=0 (no derivative).
            out_of_range: string, optional
                Determines behaviour for out of range temperatures.
                "raise": raises an IndexError exception. (default)
                "nan":   values replaced by nans.
                "extrapolate": extrapolates from closest range. Do not trust this!
 
            returns : array_like
                emfs in millivolts
        """
        
        if out_of_range not in ["raise", "nan", "extrapolate"]:
            raise ValueError("invalid out_of_range parameter",out_of_range)

        T = np.array(T, copy=False)
        emf_choices = [None]

        # First, find the range selector.
        # selector = 0 where T is underrange,
        # selector = 1 where T is in first range,
        #  ...
        # selector = N where T is in last (Nth) range,
        # selector = N+1 where T is overrange.
        tmin = self.get_tempmin()
        selector = (T >= tmin)*1
        for tmin, tmax, coefs, ec in self.table:
            selector += (T > tmax)
            # Here we go ahead and compute emf values using all ranges.
            #   this is simple but perhaps a bit inefficient.
            emf = np.polyval(np.polyder(coefs, derivative),T)
            if ec:
                # Type K thermocouple has this annoying exponential addition term,
                # corresponding to a little bump at 127 Celsius.
                # Seemingly, The reason it is there is to match a kink in the
                # first derivative.
                dT = T - ec[2]
                gauss = ec[0] * np.exp(ec[1] * dT**2)
                if derivative == 0:
                    emf += gauss
                elif derivative == 1:
                    emf += 2. * ec[1] * gauss * dT
                elif derivative == 2:
                    emf += 2. * ec[1] * gauss * (2. * ec[1] * dT**2 + 1.)
                elif derivative == 3:
                    emf += 4. * ec[1] * ec[1] * gauss * dT * (2. * ec[1] * dT**2 + 3.)
                else:
                    raise ValueError("sorry, derivatives > 3 not supported for this type.")
            emf_choices.append(emf)
        emf_choices.append(None)
        
        if out_of_range == "nan":
            emf_choices[0] = T*np.nan
            emf_choices[-1] = emf_choices[0]
        else:
            emf_choices[0]  = emf_choices[1]
            emf_choices[-1] = emf_choices[-2]

        if out_of_range == "raise":
            if np.any(selector <= 0):
                raise IndexError("Temperature underrange.")
            if np.any(selector > len(self.table)):
                raise IndexError("Temperature overrange.")

        return np.choose(selector, emf_choices)

    def emf_VK(self,T,derivative=0,out_of_range="raise"):
        """
            Convenience method.
            Works just like .emf_mVC(), except this method takes
            temperatures in kelvin, and returns emfs in volts.
            
            NOTE: the emf reference function is still zeroed at 273.15 K.
              This is unavoidable, since none of the emfs are given at 0 K.
              However since you should *always* be subtracting two values of the
              reference function, you will anyway not be affected by the offset.
        """
        T = np.array(T, copy=False) - 273.15
        return self.emf_mVC(T,out_of_range) * 0.001

    def inverse_CmV(self,mV,Tref=0.,Tstart=None):
        """
            Find the temperature corresponding to a given voltage, via zero-finding.
            First it tries to use scipy.optimize.newton;
            failing that, it uses scipy.optimize.brentq.
            (imports scipy.optimize on first use; requires scipy to be installed)
            This function might take a few milliseconds. If that's too slow for you,
            you should roll your own solution.
            
            mV: float
                Measured voltage (in millivolts) goes here.
            Tref: float
                Your reference temperature (Celsius) goes here. This allows you to
                perform cold-junction compensation. The default, Tref=0.0, corresponds to
                the reference junctions being at 0 degrees Celsius.
            Tstart: float
                Suggested starting temperature (Celsius). If not provided, uses midpoint
                of range. You can speed the search convergence by providing a
                good starting guess here. This function anyway tries its best to converge.
            
            returns: float
                Temperature (in Celsius) T, such that
                mV = emf_mVC(T) - emf_mVC(Tref)
                If this is not satisfied to within 1e-6 millivolts, an exception is raised.
        """

        global _op
        if _op == None:
            try:
                import scipy.optimize as _op
            except ImportError:
                raise NotImplementedError("Inverse lookup requires scipy.optimize. Please install scipy.")
        
        if Tstart == None:
            Tstart = 0.5*(self.get_tempmin() + self.get_tempmax())
        mVref = self.emf_mVC(Tref)
        mV = mV + mVref #compensate
        fun0 = lambda T: self.emf_mVC(T,derivative=0) - mV
        fun1 = lambda T: self.emf_mVC(T,derivative=1)
        fun2 = lambda T: self.emf_mVC(T,derivative=2)
        
        try:
            # Try newton's method first.
            T = _op.newton(fun0, Tstart, fprime=fun1, fprime2=fun2, tol=1e-6)
            if abs(self.emf_mVC(T) - mV) > 1e-6:
                raise RuntimeError
        except:
            # Any problems (range error, convergence, whatever) try brentq
            # FIXME: we are assuming the emf function is monotonic here.
            # for type B thermocouple that's not quite true, and so with that type
            # we could raise exception if someone asks for a low mV value.
            # (anyway they should not ask such a thing, as type B is meant
            #  for high temperatures.)
            try:
                # Note: brentq raises ValueError here if 
                T = _op.brentq(fun0, self.get_tempmin(), self.get_tempmax())
            except ValueError as e:
                if e.args == ("f(a) and f(b) must have different signs",):
                    raise ValueError("Compensated voltage not in allowed range.")
                else:
                    raise
            if abs(fun0(T)) > 1e-6:
                raise RuntimeError("Did not converge.")
        
        return T

#end of module
