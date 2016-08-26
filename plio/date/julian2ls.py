#!/usr/bin/env python
import sys
import math
import numpy as np


def zero360(angles, rad=False):
    """
    Convert angle to base 0-360

    Parameters
    ----------
    angles : float
             a scalar angle to convert

    rad : boolean
          flag whether angles are in radians

    Returns
    -------
    bb : float
         converted angle
    """

    if rad:
        half = math.pi
    else:
        half = 180.0

    circle = 2.0 * half

    ii = np.floor(angles / circle)
    bb = angles - circle * ii
    #Negative values to positive
    bb[bb < 0] += circle
    return bb


def julian2ls(date, marsyear=None, reverse=False):
    """

    Original IDL from Hugh Keiffer

    Parameters
    -----------
    date : numeric
           Scalar or NumPy ndarray or dates

    marsyear : float
              Mars year for use in reverse

    reverse : bool
              Reverse conversion from L_{s} to julian

    Returns
    -------
    out : numeric
          float or array of float LsubS or Julian dates

    myn : float
          If LsubS to Mars year, return the Mars year

    References
    -----------
    [1] M. Allison and M. McEwen.' A post-Pathfinder evaluation of areocentric
    solar coordinates with improved timing recipes for Mars seasonal/diurnal
    climate studies'. Plan. Space Sci., 2000, v=48, pages = {215-235},

    [2] http://www.giss.nasa.gov/tools/mars24/help/algorithm.html

    """

    if not isinstance(date, np.ndarray):
        date = np.asarray([date], dtype=np.float64)

    rec= np.array([-0.0043336633,0.0043630568,0.0039601861,0.029025116,-0.00042300026])
    dj2000 = 2451545.0  # JD of epoch J2000
    dj4m = 51544.50  # days offset from dj4 to djm
    smja = 1.523679  # semi-major axis in AU, Table 2. last digit from Ref2
    meanmotion = 0.52402075  # mean motion, degrees/day. Constant in Table 2

    a5 = np.array([71,57,39,37,21,20,18]) * 0.0001
    tau = np.array([2.2353,2.7543,1.1177,15.7866,2.1354,2.4694,32.8493])
    phi = np.array([49.409,168.173,191.837,21.736,15.704,95.528,49.095])


    if reverse:
        #Convert from lsubs to julian
        lsubs = date
        delta_lsubs = lsubs - 250.99864
        rdelta_lsubs= np.radians(delta_lsubs)
        dj4 = 51507.5 + 1.90826 * delta_lsubs -\
            20.42 * np.sin(rdelta_lsubs) +\
            0.72 * np.sin( 2. * rdelta_lsubs)  # Eq. 14

        brak = 686.9726 + 0.0043 * np.cos(rdelta_lsubs) -\
            0.0003 * np.cos(2. * rdelta_lsubs) # in brackets in Eq 14
        if marsyear is None:
            return False
        ny=marsyear + 42  # orbits of mars since 1874.0
        dj4 += brak * (ny - 66)  # last part of Eq. 14
        djtt= dj4 - dj4m  # days from J2000 TT
        tcen = djtt / 36525.0  # julian centuries from J2000
        tcor= 64.184 + tcen * (59.0 + tcen * (-51.2 + tcen * (-67.1 - tcen * 16.4)))  # TT-UTC
        djm=djtt - tcor / 86400.0  # convert correction to days and apply
        out=djm  #  out is UTC
    else:
        #Convert from julian to lsubs
        if date[0] < 1.e6:  #Is this the intended functionality - what if date[0] < and date [1] >
            djm = date
        else:
            djm = date - dj2000
        tcen = djm / 36525.0  # julian centuries from J2000
        tcor = 64.184 + tcen * (59.0 + tcen * (-51.2 + tcen * (-67.1 - tcen * 16.4)))  # TT-UTC
        djtt = djm + tcor / 86400.0  # convert correction to days and apply. get TT
        dj4 = djtt + dj4m  #  A+M's MJD
    nelements = date.size
    pbs = np.zeros(nelements)
    for i in range(nelements):
        q = 0.985626 * djtt[i]
        rq = np.radians(q / tau + phi)
        pbsi = a5 * np.cos(rq)
        pbs[i] = pbsi.sum()
    meananomoly = 19.3870 + meanmotion * djtt  # Mean anomoly M, Table 2 and Eq. 16
    rmeananomoly = np.radians(meananomoly)  # M in radians
    #Eqn of center, in brackets in eq 20 and all but the first term in eq 19. exclude pbs
    eoc = (10.691 + 3.e-7 * djtt) * np.sin(rmeananomoly)\
        + 0.623 * np.sin(2. * rmeananomoly) + 0.050 * np.sin(3. * rmeananomoly)\
        + 0.005 * np.sin(4. * rmeananomoly) + 0.0005 * np.sin(5. * rmeananomoly)

    if reverse:
        try:
            j = reverse.size
        except:
            j=0
            rev = [0]
        if j >= 5:
            #User has supplied coefficients
            rec = rev
        if j < 5 and rev[0] < 5:
            fd = 0.0
        else:
            fd=rec[0] + rec[1]* np.sin(rdelta_lsubs)\
                + rec[2] * np.sin(2. * rdelta_lsubs)\
                + rec[3] * np.sin(3. * rdelta_lsubs)\
                + rec[4] * np.sin(4. * rdelta_lsubs)
        #TODO: This looks like reversing is going to cause an fd undefined error if j >= 5
        out = out - ( pbs / meananomoly + fd)
    else:
        afms = 270.3863 + 0.52403840 * djtt # Eq. 17
        lsubs = afms + eoc + pbs              # Eq. 19 LS in degrees
        lsubs = zero360(lsubs)
        out= lsubs
        marstyear = 686.9728  # mean mars tropical  year in terrestrial days
        #marsysol=668.5991  #mars siderial year in sols
        ny = np.floor((dj4 - 5668.690)/ marstyear ) # full Mars years from 1874
        myn = ny - 42  # climate MY

    if reverse:
        return out
    else:
        return out, myn

if __name__ == '__main__':
    print(julian2ls(178, marsyear=40, reverse=True))

