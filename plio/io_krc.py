import logging
import re
import warnings

import numpy as np
import pandas as pd

try:
    import krc
except:
    import os
    import sys
    sys.path.append(os.path.basename('..'))
    import krc

idl2np_dtype = {1: np.byte, 2: np.int16, 3: np.int32, 4: np.float32,
                5: np.float64}
idl2struct = {4: 'f', 5:'d'}
archtype2struct={'sparc': None, 'bigend': '>', 'litend': '<',
          'alpha': None, 'ppc': None, 'x86': None, 'x86_64': None}


class ReadBin52(object):
    """
    Class to read a bin 52 and organize the output

    Parameters
    ----------

    filename    (str) The file to read

    Attributes
    ----------

    filename : str
               The file that was parsed

    header : str
             The header from the bin52 file

    bin52data : ndarray
                RAW bin52 binary read into an n-dim array

    ncases : int
            The number of available cases (1 based)

    nlat : int
           The number of latitudes

    nhours : int
             The number of hours

    nseasons : int
               The number of seasons

    ntau : int
           The number of opacity (tau) steps

    nalbedos : int
               The number of albedo steps

    nslope : int
             The number of slope steps

    transferedlayers : int
                       The number of transfered layers in the model

    tlabels : list
              Labels for the hourly tabel

    latelv : ndarray
             Array of model latitudes and elevations

    pd_latelv : dataframe
                Pandas dataframe reshape of latelv

    ttt : ndarray
          Hourly parameters as a vector

    pd_ttt : dataframe
             Pandas dataframe of the reshape ttt

    seasitems : ndarray
                Array of seasonal parameters (DJU5, Ls, PZREF, TAUD, SUMF)

    pd_seasitems : dataframe
                   Pandas dataframe reshape of seasitems

    ddd : ndarray
          Model temperatures by layer

    pd_ddd : dataframe
             Pandas dataframe reshape of ddd

    pd_itemg : dataframe
               Pandas dataframe of ggg
    """

    def __init__(self, filename, headerlen=512):

        # Get or setup the logging object
        self.logger = logging.getLogger(__name__)

        self.filename = filename
        self.readbin5(headerlen)

        assert(self.ncases == self.bin52data.shape[0])

    def definekrc(self, what='KRC', endianness='<'):
        """
        Defines a custom binary data structure for the KRC files.
        """
        if what == 'KRC':
            numfd = 96  # Size of floats of T-dependent materials
            numid = 40  # size of "  " integers
            numld = 20  # size of "  " logicals
            maxn1 = 30  # dimension of layers
            maxn2 = 384 * 4  # dimensions of times of day
            maxn3 = 16  # dimensions of iterations days
            maxn4 = self.nlats * 2 - 1  # dimensions of latitudes
            maxn5 = 161 # dimensions of seasons
            maxn6 = 6  # dimensions of saved years
            maxnh = self.nhours  # dimensions of saved times of day
            maxbot = 6  # dimensions of time divisions
            numtit = 20  # number of 4-byte words in TITLE
            numday = 5  # number of 4-byte words in DAY
            e = endianness
            self.logger.debug(self.structdtype)

            #Define the structure of the KRC file
            if self.structdtype == '<f':
                self._krcstructure = np.dtype([('fd','{}{}f'.format(e, numfd)),
                                        ('id','{}{}i'.format(e, numid)),
                                        ('ld','{}{}i'.format(e, numld)),
                                        ('title','{}{}a'.format(e, 4 * numtit)),
                                        ('daytime','{}{}a'.format(e, 4 * numday)),
                                        ('alat','{}{}f4'.format(e, maxn4)),
                                        ('elev','{}{}f4'.format(e,maxn4))])
            elif self.structdtype == '<d':
                self._krcstructure = np.dtype([('fd','{}{}d'.format(e, numfd)),
                                               ('alat','{}{}d'.format(e, maxn4)),
                                               ('elev','{}{}d'.format(e,maxn4) ),
                                               ('id','{}{}i'.format(e, numid)),
                                               ('ld','{}{}i'.format(e, numld)),
                                               ('title','{}{}a'.format(e, 4 * numtit) ),
                                               ('daytime','{}{}a'.format(e, 4 * numday))])

    def readbin5(self, headerlen):
        """
        Reads the type 52 file containing KRC output.

        Tested with KRC version 2.2.2.  Note that the output format
        can change

        Parameters
        ----------
        filename    (str) Full PATH to the file
        """
        def _parse_header():
            header = re.findall(b'\d+', fullheader.split(b'<<')[0])
            header = list(map(int, header))
            self.ndim = header[0]
            self.nhours = header[1]
            self.nvariables = header[2]
            self.nlats = header[3]
            self.nseasons = header[4] - 1
            self.headerlength = header[8]
            self.ncases = header[0 + self.ndim]
            self.header = header

            # Compute how large each case is
            self.casesize = self.nhours
            if self.ndim > 1:
                for k in range(1, self.ndim - 1):
                    self.casesize *= header[k + 1]

        def _parse_front():
            # Read the front matter
            front = np.fromfile(bin5, dtype=self.structdtype, count=4).astype(np.int)
            self.words_per_krc = front[0]
            self.ndx = front[2]

        def _read_data():
            bin5.seek(self.headerlength)
            self.bin52data = np.fromfile(bin5,
                                         dtype=self.structdtype)
            self.logger.debug(len(self.bin52data))

            indices = arraysize[1: -1]
            self.bin52data = self.bin52data.reshape(indices[: : -1])

        def _get_version():
            ver = re.findall(b'\d+', head)
            ver = list(map(int, ver))
            self.version = ver[: 3]

        #Add smarter filename handling
        with open(self.filename, 'rb') as bin5:

            #To handle endianness and architectures
            archbytes = 8
            c_end = 5

            fullheader = bin5.read(headerlen)
            _parse_header()

            arraysize = self.header[0: self.ndim + 2]
            arraydtypecode = arraysize[arraysize[0] + 1]
            try:
                arraydtype = idl2np_dtype[arraydtypecode]
                self.logger.debug("Dtype: ", arraydtype)
            except KeyError:
                self.logger.error("Unable to determine input datatype.")

            assert(len(self.header) == self.ndim + 4)

            if self.headerlength > 512:
                warnings.Warn('Expected header to be 512 bytes, is {} bytes'.format(self.headerlength))
                return

            #Get the endianness of the input file and the data type (32 or 64 bit)
            archstart = self.headerlength - (archbytes + c_end)
            archend = self.headerlength - c_end
            encodingarch = fullheader[archstart: archend].rstrip()
            encodingarch = encodingarch.decode()

            self._endianness = archtype2struct[encodingarch]
            self.structdtype = self._endianness + idl2struct[arraydtypecode]

            #Get the date and head debug
            idx2 = fullheader.find(b'>>')
            idx1 = idx2 - 21
            self.date = fullheader[idx1: idx1 + 20]
            head = fullheader[idx2 + 2:  self.headerlength - (archbytes + c_end) - 3 - idx2]
            head = head.rstrip()

            # Parse the header
            _get_version()
            _parse_front()
            _read_data()

    def readcase(self, case=1):
        """
        Read a single dimension (case) from a bin52 file.

        Parameters
        -----------
        case       (int) The case to be extracted

        Returns
        -------
        casearr    (ndarray) The extracted KRC model for
                             the case.
        """

        if self.structdtype == '<f':
            j = 512 + (1 - 1) * 4 * self.casesize + 16
        elif self.structdtype == '<d':
            j = 512 + (1 - 1) * 4 * self.casesize + 32
        with open(self.filename, 'r') as krc:
            # Skip to the correct case
            krc.seek(j)
            self.definekrc('KRC')
            structarr = np.fromfile(krc, dtype=self._krcstructure, count=1)
        if self.structdtype == '<f':
            self.structarr = {'fd': structarr[0][0],
                'id': structarr[0][1],
                'ld': structarr[0][2],
                'title': structarr[0][3],
                'date': structarr[0][4],
                'alat': structarr[0][5],
                'elevation': structarr[0][6]
                }
        elif self.structdtype == '<d':
            self.structarr = {'fd': structarr[0][0],
                    'alat': structarr[0][1],
                    'elevation': structarr[0][2],
                    'id': structarr[0][3],
                    'ld': structarr[0][4],
                    'title': structarr[0][5],
                    'date':structarr[0][6]}

        self.nlayers = nlayers = self.structarr['id'][0]
        itemt = ['Final Hourly Surface Temp.',
                 'Final Hourly Planetary Temp.',
                 'Final Hourly Atmospheric Temp.',
                 'Hourly net downward solar flux [W/m^2]',
                 'Hourly net downward thermal flux [W/m^2]']

        itemu = ['Lat', 'Elev']
        itemv = ['Current Julian date (offset from J2000.0)',
                 'Seasonal longitude of Sun (in degrees)',
                 'Current surface pressure at 0 elevation (in Pascals)',
                 'Mean visible opacity of dust, solar wavelengths',
                 'Global average columnar mass of frost [kg /m^2]']
        itemd = ['Tmin', 'Tmax']
        itemg = ['# Days to Compute Soln.',
         'RMS Temp. Change on Last Day',
         'Predicted Final Atmospheric Temp.',
         'Predicted frost amount, [kg/m^2]',
         'Frost albedo (at the last time step)',
         'Mean upward heat flow into soil surface on last day, [W/m^2]']

        self.glabels = itemg
        self.tlabels = itemt
        self.ulabels = itemu
        self.vlabels = itemv
        self.dlabels = itemd

        nlat = len(self.structarr['alat'])
        transferedlayers = nlayers - 1
        if self.nhours - 3 < transferedlayers:
            transferedlayers = self.nhours - 3
        wordsperlat = self.nhours * self.nvariables
        wordsperseason = wordsperlat * self.nlats

        if self.nvariables != len(itemt) + len(itemd):
            self.logger.error("Error! Size mismatch")

        # Each case has a header that must be extracted:
        header = self.bin52data[:,0:self.ndx,: ,: ,: ].reshape(self.ncases,
                                                               wordsperseason * self.ndx)
        #krccomm
        k = 4 + self.words_per_krc + 5 * self.nseasons
        krcc = header[:, 4: 4 + self.words_per_krc]

        # Build a dataframe of the seasonal information
        seasitems = header[:, 4 + self.words_per_krc: k ].reshape(self.ncases,
                                                                  len(itemv),
                                                                  self.nseasons)
        # Good to HERE.
        caseidx = np.repeat(np.arange(self.ncases), self.nseasons)
        seasonidx = np.repeat(np.arange(self.nseasons), self.ncases)
        flt_seasitems = seasitems.reshape(len(self.vlabels),
                                          self.ncases * self.nseasons)
        self.seasitems = pd.DataFrame(flt_seasitems,
                                      columns=[caseidx,seasonidx],
                                      index=[self.vlabels])
        self.seasitems.columns.names = ['Case', 'Season']

        # TODO: Can nlat_include_null be replaced with self.nlats?
        nlat_include_null = len(self.structarr['alat'])
        prelatwords = self.words_per_krc - 2 * nlat_include_null
        #All latitudes
        #Hugh made some change to the krcc format, but I cannot find documentation...
        if self.structdtype == '<f':
            alllats = krcc[:,prelatwords:].reshape(2, nlat_include_null, ncases)
        elif self.structdtype == '<d':
            alllats = krcc[:,96:170].reshape(2, nlat_include_null, self.ncases)
        self.alllats = alllats
        #Latitudes and elevations for each case
        self.latelv = alllats[: ,0: nlat]
        if self.latelv.shape[-1] == 1:
            self.latelv = self.latelv[:,:,0]
        self.pd_latelv = pd.DataFrame(self.latelv.T, columns=['Latitude', 'Elevation'])
        wordspercase = wordsperseason * self.nseasons  # arrshp[1] = nseasons
        jword = [4,wordspercase, self.ncases]


        self.ttt = self.bin52data[: ,self.ndx: ,: ,0: len(itemt),: ].reshape(self.ncases,
                                                                             self.nseasons,
                                                                             self.nlats,
                                                                             len(itemt),
                                                                             self.nhours)
        self.hourly2dataframe()

        layeritems = self.bin52data[: , self.ndx: , : , 5: 7, : ]
        self.latitems = layeritems[: ,: ,: ,: ,0: 3].reshape(self.ncases,
                                                             self.nseasons,
                                                             self.nlats, len(itemg))
        self.latitems2dataframe()

        self.ddd = layeritems[: ,: ,: ,: ,3: 3 + transferedlayers].reshape(self.ncases,
                                                                               self.nseasons,
                                                                               self.nlats,
                                                                               len(itemd),
                                                                               transferedlayers)
        self.transferedlayers = transferedlayers
        self.layer2dataframe()

    def latitems2dataframe(self):
        """
        Converts Latitude items to a dataframe
        """
        idxcount = self.nseasons * self.nlats * self.ncases
        idxpercase = self.nseasons * self.nlats
        caseidx = np.empty(idxcount)
        for c in range(self.ncases):
            start = c * idxpercase
            caseidx[start:start+idxpercase] = np.repeat(c, idxpercase)
        nseasvect = np.arange(self.nseasons)
        seasonidx = np.repeat(np.arange(self.nseasons), self.nlats)
        latidx = np.tile(self.latelv[0].ravel(), self.nseasons)

        self.pd_itemg = pd.DataFrame(self.latitems.reshape(self.nseasons * self.nlats, -1).T,
                                     columns=[caseidx, seasonidx, latidx], index=self.glabels)
        self.pd_itemg.columns.names = ['Case','Season', 'Latitude']

    def layer2dataframe(self):
        """
        Converts layeritems into
        """
        self.logger.debug((self.nseasons, self.nlats, self.transferedlayers, self.ncases))
        idxcount = self.nseasons * self.nlats * self.transferedlayers * self.ncases
        caseidx = np.empty(idxcount)
        idxpercase = self.nseasons * self.nlats * self.transferedlayers
        for c in range(self.ncases):
            start = c * idxpercase
            caseidx[start:start + idxpercase] = np.repeat(c, idxpercase)

        seasonidx = np.repeat(np.arange(self.nseasons), idxcount / self.nseasons / self.ncases)
        nlatidx = np.repeat(self.latelv[0].ravel(), idxcount / self.transferedlayers / self.ncases)
        tranlayeridx = np.tile(np.repeat(np.arange(self.transferedlayers), self.nlats), self.nseasons)
        self.pd_ddd = pd.DataFrame(self.ddd.reshape(idxcount, -1).T, index=[self.dlabels], columns=[caseidx, seasonidx, nlatidx, tranlayeridx])
        self.pd_ddd.columns.names = ['Case', 'Season', 'Latitude', 'Layer']

    def seas2dataframe(self):
        """
        converts seasitems 'vvv' vector to a
        labelled Pandas dataframe
        """


    def hourly2dataframe(self):
        """
        Converts the hourly 'ttt' vector to a
        labelled Pandas dataframe.
        """
        reshapettt = np.swapaxes(self.ttt.reshape(self.ncases * self.nseasons * self.nlats, len(self.tlabels), self.nhours),1,2)
        shp = reshapettt.shape
        reshapettt = reshapettt.reshape((shp[0] * shp[1], shp[2])).T
        #Indices
        caseidx = np.repeat(np.arange(self.ncases), self.nseasons * self.nlats * self.nhours)
        seasonidx = np.tile(np.repeat(np.arange(self.nseasons), self.nlats * self.nhours), self.ncases)
        latidx = np.tile(np.repeat(self.latelv[0].ravel(), self.nhours), self.nseasons)
        houridx = np.tile(np.tile(np.tile(np.arange(self.nhours), self.nlats), self.nseasons), self.ncases)

        #DataFrame
        self.pd_ttt = pd.DataFrame(reshapettt.T,
                                   index=[caseidx, seasonidx, latidx, houridx],
                                   columns=self.tlabels)
        self.pd_ttt.index.names = ['Case', 'Season', 'Latitude', 'Hour']
        self.temperature_data = self.pd_ttt
        #self.pd_ttt = self.pd_ttt.T

class ReadTds(object):
    def __init__(self):
        pass