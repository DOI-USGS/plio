""" For more information about astronomical date specifications,
consult a reference source such as
U{this page <http://tycho.usno.navy.mil/systime.html>} provided by
the US Naval Observatory.

Constants and formulae in this module were taken from the times.h
include file of the tpm package by Jeff Percival, to ensure compatibility.

"""

import types
import datetime

#first define some globally-useful constants
B1950 = 2433282.42345905
J2000 = 2451545.0
CB    = 36524.21987817305
CJ    = 36525.0
MJD_0 = 2400000.5

def jyear2jd(jyear):
    """
    @param jyear: decimal Julian year
    @type jyear: float
    @return: Julian date
    @rtype: float
    """
    return (J2000 + ((jyear)-2000.0)*(CJ/100.0))

def jd2jyear(jd):
    """
    @return: decimal Julian year
    @rtype: float
    @param jd: Julian date
    @type jd: float
    """
    return (2000.0 + ((jd)-J2000)*(100.0/CJ))

def byear2jd(byear):
    """
    @param byear: decimal Besselian year
    @type byear: float
    @return: Julian date
    @rtype: float
    """
    return (B1950 + ((byear)-1950.0)*(CB/100.0))

def utc2jd(utc):
    """
    Convert UTC to Julian date.

    Conversion translated from TPM modules utcnow.c and gcal2j.c, which
    notes that the algorithm to convert from a gregorian proleptic calendar
    date onto a julian day number is taken from
    The Explanatory Supplement to the Astronomical Almanac (1992),
    section 12.92, equation 12.92-1, page 604.

    @param utc: UTC (Universal Civil Time)
    @type utc: U{datetime<http://docs.python.org/lib/datetime.html>} object
    @return: Julian date (to the nearest second)
    @rtype: float



    """

##  But, beware of different rounding behavior between C and Python!
##    - integer arithmetic truncates -1.07 to -2 in Python; to -1 in C
##    - to reproduce C-like behavior in Python, do the math with float
##  arithmetic, then explicitly cast to int.


    y=float(utc.year)
    m=float(utc.month)
    d=float(utc.day)
    hr=utc.hour
    min=utc.minute
    sec=utc.second

    #Address differences between python and C time conventions
    #       C:                Python datetime
    # 0 <= mon  <= 11        1 <= month <= 12
    #

    #C code to get the julian date of the start of the day */
    #takes as input 1900+ptm->tm_year, ptm->tm_mon+1, ptm->tm_mday
    # So we can use just (year, month, mday)

    mterm=int((m-14)/12)
    aterm=int((1461*(y+4800+mterm))/4)

    bterm=int((367*(m-2-12*mterm))/12)

    cterm=int((3*int((y+4900+mterm)/100))/4)

    j=aterm+bterm-cterm+d
    j -= 32075
    #offset to start of day
    j -= 0.5


#    print "h/m/s: %f/%f/%f"%(hr,min,sec)

    #Apply the time
    jd = j + (hr + (min + (sec/60.0))/60.0)/24.0

    return jd

def AstroDate(datespec=None):
    """AstroDate can be used as a class for managing astronomical
    date specifications (despite the fact that it was implemented
    as a factory function) that returns either a BesselDate or a
    JulianDate, depending on the properties of the datespec.

    AstroDate was originally conceived as a Helper class for the
    Position function for use with pytpm functionality, but also as a
    generally useful class for managing astronomical date specifications.

    The philosophy is the same as Position: to enable the user to specify
    the date once and for all, and access it in a variety of styles.

    @param datespec: Date specification as entered by the user. Permissible
    specifications include:
         - Julian year: 'J1997', 'J1997.325', 1997.325: return a JulianDate
         - Besselian year: 'B1950','B1958.432': return a BesselDate
         - Julian date: 'JD2437241.81', '2437241.81', 2437241.81: return a JulianDate
         - Modified Julian date: 'MJD37241.31': returns a JulianDate
         - A U{datetime <http://docs.python.org/lib/datetime.html>} object: return a JulianDate (assumes input time is UTC)
         - None: returns the current time as a JulianDate

    @type datespec: string, float, integer,  U{datetime <http://docs.python.org/lib/datetime.html>}, or None

    @rtype: L{JulianDate} or L{BesselDate}

    @raise ValueError: Raises an exception if the date specification is a
    string, but begins with a letter that is not 'B','J','JD', or 'MJD'
    (case insensitive).

    @todo: Add math functions! Addition, subtraction.
    @todo: Is there a need to support other date specifications?
    eg FITS-style dates?
    """

    if datespec is None:
        return JulianDate(datetime.datetime.utcnow())

    try:
        dstring=datespec.upper()
        if dstring.startswith('B'):
            #it's a Besselian date
            return BesselDate(datespec)
        elif ( dstring.startswith('JD') or
               dstring.startswith('MJD') or
               dstring.startswith('J') ):
            #it's Julian, one way or another
            return JulianDate(datespec)
        elif dstring[0].isalpha():
            raise ValueError("Invalid system specification: must be B, J, JD, or MJD")
        else: #it must be a numeric string: assume Julian
            return JulianDate(datespec)

    except AttributeError:
        #if no letter is specified, assume julian
        return JulianDate(datespec)



class JulianDate:
    """
    @ivar year: Decimal Julian year
    @type year: float

    @ivar jd: Julian date
    @type jd: float

    @ivar mjd: Modified Julian Date
    @type mjd: float

    @ivar datespec: Date specification as entered by the user
    """

    def __init__(self,datespec):
        self.datespec=datespec

        if isinstance(datespec,datetime.datetime):
            #Note assumption that datespec is already in UTC
            self.jd=utc2jd(datespec)
            self.mjd=self.jd-MJD_0
            self.year=jd2jyear(self.jd)

        elif type(datespec) is types.StringType:
            if datespec.upper().startswith('JD'):
                #it's a julian date
                self.jd=float(datespec[2:])
                self.mjd=self.jd-MJD_0
                self.year=jd2jyear(self.jd)
            elif datespec.upper().startswith('MJD'):
                #it's a modified julian date
                self.mjd=float(datespec[3:])
                self.jd=self.mjd+MJD_0
                self.year=jd2jyear(self.jd)
            elif datespec.upper().startswith('J'):
                #it's a julian decimal year
                self.year=float(datespec[1:])
                self.jd=jyear2jd(self.year)
                self.mjd=self.jd-MJD_0

            elif not datespec[0].isalpha():
                #somebody put a numeric date in quotes
                datespec=float(datespec)
                if datespec < 10000:
                    #it's a year. Assume julian.
                    self.year=float(datespec)
                    self.jd=jyear2jd(self.year)
                    self.mjd=self.jd-MJD_0
                else:
                    #it's a date. Assume JD not MJD.
                    self.jd=float(datespec)
                    self.mjd=self.jd+MJD_0
                    self.year=jd2jyear(self.jd)
            else:
                print("help, we are confused")

        else: #it's a number
            if datespec < 10000:
                #it's a year. Assume julian.
                self.year=float(datespec)
                self.jd=jyear2jd(self.year)
                self.mjd=self.jd-MJD_0
            else:
                #it's a date. Assume JD not MJD.
                self.jd=datespec
                self.mjd=self.jd+MJD_0
                self.year=jd2jyear(self.jd)

    def __repr__(self):
        return str(self.datespec)

    def __equals__(self,other):
        """ All comparisons will be done based on jd attribute """
        return self.jd == other.jd

    def __lt__(self,other):
        return self.jd < other.jd

    def __gt__(self,other):
        return self.jd > other.jd

    def __le__(self,other):
        return self.jd <= other.jd

    def __ge__(self,other):
        return self.jd >= other.jd

    def byear(self):
        """ Return Besselian year based on previously calculated
        julian date.
        @return: decimal Besselian year
        @rtype: float
        """
        ans=(1950.0 + ((x)-B1950)*(100.0/CB))
        return ans


class BesselDate:
    """
    @ivar year: Decimal Besselian year
    @type year: float

    @ivar jd: Julian date
    @type jd: float

    @ivar mjd: Modified Julian Date
    @type mjd: float

    @ivar datespec: Date specification as entered by the user

    """

    def __init__(self,datespec):
        self.datespec=datespec
        try:
            self.year=float(datespec)
        except ValueError:
            self.year=float(datespec[1:])
        self.jd=byear2jd(self.year)
        self.mjd=self.jd-MJD_0

    def __equals__(self,other):
        """ All comparisons will be done based on jd attribute """
        return self.jd == other.jd

    def __lt__(self,other):
        return self.jd < other.jd

    def __gt__(self,other):
        return self.jd > other.jd

    def __le__(self,other):
        return self.jd <= other.jd

    def __ge__(self,other):
        return self.jd >= other.jd


    def jyear(self):
        """ Return the julian year using the already-converted
        julian date
        @return: Decimal Julian year
        @rtype: float
        """
        ans = jd2jyear(self.jd)
        return ans

