import logging
import re
import warnings

import numpy as np
import pandas as pd

idl2np_dtype = {1: np.byte, 2: np.int16, 3: np.int32, 4: np.float32,
                5: np.float64}
idl2struct = {4: 'f', 5:'d'}
archtype2struct={'sparc': None, 'bigend': '>', 'litend': '<',
          'alpha': None, 'ppc': None, 'x86': None, 'x86_64': None}


class ReadBin52(object):
    """
    Class to read a bin 52 and organize the output


    Attributes
    ----------
    bin52data : ndarray
                The raw, n-dimensional KRC data

    casesize : int
               The number of bytes in each KRC case

    date : bytes
           The date the read file was created

    ddd : ndarray
          Raw temperature data

    ddd_pd : dataframe
             A pandas dataframe of surface temperature data

    filename : str
               The name of the KRC file that was input

    header : list
             The KRC header unpack to a list of ints

    headerlength : int
                   The length, in bytes, of the KRC header

    ncases : int
             The number of different cases the model was run for

    ndim : int
           TBD

    ndx : int
          The number of indices for a single KRC run

    nhours : int
             The number of hour bins per 24 Mars hours

    nlats : int
            The number of valid, non-zero latitude bins

    nseasons : int
               The number of seasons the model was run for

    nvariables : int
                 The number of variables contained within the KRC
                 lookup table

    structdtype : str
                  Describing endianess and data type

    temperature_data : dataframe
                       A multi-indexed dataframe of surface temperatures

    transferedlayers : int
                       The number of KRC transfered layers

    version : list
              The krc verison used to create the file in the form
              [major, minor, release]

    words_per_krc : int
                    The number of bytes per krc entry
    """

    def __init__(self, filename, headerlen=512):
        """
        Parameters
        ----------
        filename : str
                   The file to read

        headerlength : int
                       The length, in bytes, of the text header.
                       Default: 512
        """
        # Get or setup the logging object
        self.logger = logging.getLogger(__name__)

        self.filename = filename
        self.readbin5(headerlen)
        print(self.ncases)
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
                self._krcstructure= np.dtype([('fd','{}{}f'.format(e, numfd)),
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
            print(self.header)
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

        def _read_metadata():
            if self.structdtype == '<f':
                j = self.headerlength + 16  # Skip header plus 1 16bit entry
            elif self.structdtype == '<d':
                j = self.headerlength + 32 # Skip header plus 1 32bit entry

            bin5.seek(j)
            self.definekrc('KRC')
            structarr = np.fromfile(bin5, dtype=self._krcstructure, count=1)

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

        def _get_version():
            ver = re.findall(b'\d+', head)
            ver = list(map(int, ver))
            self.version = ver[: 3]

        with open(self.filename, 'rb') as bin5:

            #To handle endianness and architectures
            archbytes = 8
            c_end = 5

            fullheader = bin5.read(headerlen)
            _parse_header()
            print(self.header)
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
            _read_metadata()


    def readcase(self, case=0):
        """
        Read a single dimension (case) from a bin52 file.

        Parameters
        -----------
        case : int
               The case to be extracted
        """

        def latitems2dataframe():
            """
            Converts Latitude items to a dataframe
            """
            columns = ['# Days to Compute Soln.',
                      'RMS Temp. Change on Last Day',
                      'Predicted Final Atmospheric Temp.',
                      'Predicted frost amount, [kg/m^2]',
                      'Frost albedo (at the last time step)',
                      'Mean upward heat flow into soil surface on last day, [W/m^2]']

            # Grab the correct slice from the data cube and reshape
            latitems = layeritems[: ,: ,: ,: ,0: 3].reshape(self.ncases,
                                                     self.nseasons,
                                                     self.nlats, len(columns))

            # Multi-index generation
            idxcount = self.nseasons * self.nlats * self.ncases
            idxpercase = self.nseasons * self.nlats
            caseidx = np.empty(idxcount)
            for c in range(self.ncases):
                start = c * idxpercase
                caseidx[start:start+idxpercase] = np.repeat(c, idxpercase)
            nseasvect = np.arange(self.nseasons)
            seasonidx = np.repeat(np.arange(self.nseasons), self.nlats)
            latidx = np.tile(self.latitudes.values.ravel(), self.nseasons)

            # Pack the dataframe
            self.latitude = pd.DataFrame(latitems.reshape(self.nseasons * self.nlats, -1),
                                        index=[caseidx, seasonidx, latidx],
                                        columns=columns)

            self.latitude.index.names = ['Case','Season' ,'Latitude']

        def layer2dataframe():
            """
            Converts layeritems into
            """
            columns = ['Tmin', 'Tmax']

            ddd = layeritems[: ,: ,: ,: ,3: 3 + self.transferedlayers].reshape(self.ncases,
                                                                   self.nseasons,
                                                                   self.nlats,
                                                                   len(columns),
                                                                   self.transferedlayers)

            idxcount = self.nseasons * self.nlats * self.transferedlayers * self.ncases
            caseidx = np.empty(idxcount)
            idxpercase = self.nseasons * self.nlats * self.transferedlayers
            for c in range(self.ncases):
                start = c * idxpercase
                caseidx[start:start + idxpercase] = np.repeat(c, idxpercase)

            seasonidx = np.repeat(np.arange(self.nseasons), idxcount / self.nseasons / self.ncases)
            nlatidx = np.repeat(self.latitudes.values.ravel(), idxcount / self.transferedlayers / self.ncases)
            tranlayeridx = np.tile(np.repeat(np.arange(self.transferedlayers), self.nlats), self.nseasons)
            self.layers = pd.DataFrame(ddd.reshape(idxcount, -1),
                                       columns=columns,
                                       index=[caseidx, seasonidx, nlatidx, tranlayeridx])
            self.layers.index.names = ['Case', 'Season', 'Latitude', 'Layer']

        def latelv2dataframes():
            """
            Convert the latitude and elevation arrays to dataframes
            """
            #All latitudes
            #Hugh made some change to the krcc format, but I cannot find documentation...
            if self.structdtype == '<f':
                alllats = krcc[:,prelatwords:].reshape(2, nlat_include_null, self.ncases)
            elif self.structdtype == '<d':
                alllats = krcc[:,96:170].reshape(2, nlat_include_null, self.ncases)
                #Latitudes and elevations for each case
            latelv = alllats[: ,0: nlat]
            if latelv.shape[-1] == 1:
                latelv = latelv[:,:,0]
            self.latitudes = pd.DataFrame(latelv[0], columns=['Latitude'])
            self.elevations = pd.DataFrame(latelv[1], columns=['Elevation'])

        def season2dataframe():
            columns = ['Current Julian date (offset from J2000.0)',
                 'Seasonal longitude of Sun (in degrees)',
                 'Current surface pressure at 0 elevation (in Pascals)',
                 'Mean visible opacity of dust, solar wavelengths',
                 'Global average columnar mass of frost [kg /m^2]']

            # Build a dataframe of the seasonal information
            seasitems = header[:, 4 + self.words_per_krc: k ].reshape(self.ncases,
                                                                      len(columns),
                                                                      self.nseasons)
            caseidx = np.repeat(np.arange(self.ncases), self.nseasons)
            seasonidx = np.repeat(np.arange(self.nseasons), self.ncases)
            flt_seasitems = seasitems.reshape(len(self.vlabels),
                                              self.ncases * self.nseasons)
            self.seasons = pd.DataFrame(flt_seasitems,
                                          index=[caseidx,seasonidx],
                                          columns=columns)
            self.seasons.index.names = ['Case', 'Season']

        def hourly2dataframe():
            """
            Converts the hourly 'ttt' vector to a
            labelled Pandas dataframe.
            """
            columns = ['Final Hourly Surface Temp.',
                     'Final Hourly Planetary Temp.',
                     'Final Hourly Atmospheric Temp.',
                     'Hourly net downward solar flux [W/m^2]',
                     'Hourly net downward thermal flux [W/m^2]']
            ttt = self.bin52data[: ,self.ndx: ,: ,0: len(columns),: ].reshape(self.ncases,
                                                                         self.nseasons,
                                                                         self.nlats,
                                                                         len(columns),
                                                                         self.nhours)

            reshapettt = np.swapaxes(ttt.reshape(self.ncases * self.nseasons * self.nlats,
                                                 len(columns),
                                                 self.nhours),1,2)
            shp = reshapettt.shape
            reshapettt = reshapettt.reshape((shp[0] * shp[1], shp[2])).T
            #Indices
            caseidx = np.repeat(np.arange(self.ncases), self.nseasons * self.nlats * self.nhours)
            seasonidx = np.tile(np.repeat(np.arange(self.nseasons), self.nlats * self.nhours), self.ncases)
            latidx = np.tile(np.repeat(self.latitudes.values.ravel(), self.nhours), self.nseasons)
            houridx = np.tile(np.tile(np.tile(np.arange(self.nhours), self.nlats), self.nseasons), self.ncases)

            #DataFrame
            self.temperatures = pd.DataFrame(reshapettt.T,
                                       index=[caseidx, seasonidx, latidx, houridx],
                                       columns=columns)
            self.temperatures.index.names = ['Case', 'Season', 'Latitude', 'Hour']



        self.nlayers = nlayers = self.structarr['id'][0]
        nlat = len(self.structarr['alat'])
        self.transferedlayers = nlayers - 1
        if self.nhours - 3 < self.transferedlayers:
            self.transferedlayers = self.nhours - 3

        wordsperlat = self.nhours * self.nvariables
        wordsperseason = wordsperlat * self.nlats

        # Each case has a header that must be extracted:
        header = self.bin52data[:,0:self.ndx,: ,: ,: ].reshape(self.ncases,
                                                               wordsperseason * self.ndx)
        k = 4 + self.words_per_krc + 5 * self.nseasons
        krcc = header[:, 4: 4 + self.words_per_krc]

        nlat_include_null = len(self.structarr['alat'])
        prelatwords = self.words_per_krc - 2 * nlat_include_null

        wordspercase = wordsperseason * self.nseasons

        # Extract the latitude and elevation metadata
        latelv2dataframes()

        #Extract the hourly temperature data
        hourly2dataframe()

        # Extract by layer data from the data cube
        layeritems = self.bin52data[: , self.ndx: , : , 5: 7, : ]
        latitems2dataframe()
        layer2dataframe()



class ReadTds(object):

    def __init__(self, filename, headerlength=512):
        """
        Parameters
        ----------
        filename : str
                   The file to read

        headerlength : int
                       The length, in bytes, of the text header.
                       Default: 512
        """
        # Get or setup the logging object
        self.logger = logging.getLogger(__name__)

        self.filename = filename
        self.readbin5(headerlen)
        print(self.ncases)
        assert(self.ncases == self.bin52data.shape[0])