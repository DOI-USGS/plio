import itertools
import logging
import re
import warnings

import numpy as np
import pandas as pd

from plio.utils.utils import compute_log_values

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
        assert(self.ncases == self.bin52data.shape[0])

    def definekrc(self, what='KRC', endianness='<'):
        """
        Defines a custom binary data structure for the KRC files.
        """
        if what == 'KRC':
            numfd = 96  # Size of floats of T-dependent materials
            numid = 40  # size of "  " integers
            numld = 20  # size of "  " logicals
            maxn1 = 50 #30  # dimension of layers
            maxn2 = 393216 #384 * 4  # dimensions of times of day
            maxn3 = 16  # dimensions of iterations days
            maxn4 = self.nlats #* 2 #- 1  # dimensions of latitudes
            maxn5 = 161 # dimensions of seasons
            maxn6 = 6  # dimensions of saved years
            maxnh = self.nhours  # dimensions of saved times of day
            maxbot = 14 #6  # dimensions of time divisions
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
                print(krcc.shape)
                alllats = krcc[:,96:170].reshape(self.ncases, 2, nlat_include_null)
                #Latitudes and elevations for each case
            latelv = alllats[: ,0: nlat]
            if latelv.shape[-1] == 1:
                latelv = latelv[:,:,0]
            self.latitudes = pd.DataFrame(latelv[0][0], columns=['Latitude'])
            self.elevations = pd.DataFrame(latelv[0][1], columns=['Elevation'])

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
            flt_seasitems = seasitems.reshape(len(columns),
                                              self.ncases * self.nseasons)
            self.seasons = pd.DataFrame(flt_seasitems.T,
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

        # Extract the seasons
        season2dataframe()

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

        self.filename = filename
        self.headerlength = headerlength
        self.fhandle = open(self.filename, 'rb')
        self._parse_header()
        if self.version <= '3.2.1':
            multi = 32
        else:
            multi = 16
            
        datastart = int(self.header.loc['N4'] * self.header.loc['N24'] * multi)
        self.data = self.read(self.filename, datastart)
    
    def _parse_header(self):
        """
        Parse a KRC header to programmatically get the input parameters, 
        latitudes, elevations, and verison number.
        """
        fp = np.fromfile(self.fhandle, count=64, dtype=np.float64)
        fp_cols = ['ALBEDO', 'EMISS', 'INERTIA', 'COND2', 'DENS2', 'PERIOD', 'SPEC_HEAT', 'DENSITY',
                   'CABR', 'AMW', 'SatPrA', 'PTOTAL', 'FANON', 'TATM', 'TDEEP', 'SpHeat2',
                   'TAUD/PHT', 'DUSTA', 'TAURAT', 'TWILI', 'ARC2/Pho', 'ARC3/Safe', 'SLOPE', 'SLOAZI',
                   'TFROST', 'CFROST', 'AFROST', 'FEMIS', 'AF1', 'AF2', 'FROEXT', 'SatPrB',
                   'RLAY', 'FLAY', 'CONVF', 'DEPTH', 'DRSET', 'DDT', 'GGT', 'DTMAX',
                   'DJUL', 'DELJUL', 'SOLARDEC', 'DAU', 'LsubS', 'SOLCON', 'GRAV', 'AtmCp',
                   'ConUp0', 'ConUp1', 'ConUp2', 'ConUp3', 'ConLo0', 'ConLo1', 'ConLo2', 'ConLo3',
                   'SphUp0', 'SphUp1', 'SphUp2', 'SphUp3', 'SphLo0', 'SphLo1', 'SphLo2', 'SphLo3']
        
        self.fhandle.seek(1360)
        ip = np.fromfile(self.fhandle, count=20, dtype=np.int32)
        ip_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N24', 'IIB', 'IC2',
                   'NRSET', 'NMHA', 'NRUN', 'JDISK', 'IDOWN', 'FlxP14', 'TUN/Flx15', 'KPREF',
                   'K4OUT', 'JBARE', 'Notif', 'IDISK2']
        self.fhandle.seek(768)
        self.latitudes = np.fromfile(self.fhandle, count=37, dtype=np.float64)
        self.elevations = np.fromfile(self.fhandle, count=37, dtype=np.float64)
        # This is super hard coded to the format...
        self.fhandle.seek(1608)
        self.version = str(self.fhandle.read(3))
        
        self.header = pd.Series(np.concatenate([fp, ip]), index=fp_cols + ip_cols)


    def read(self, infile, datastart):
        """
        Read the TDS file in as a numpy array.

        Parameters
        ----------
        infile : str
                 Input file PATH
        datastart : int
                    The binary offset to start reading at
        Returns
        -------
               : ndarray
                 n x 37 x (nseason * 2) array
        """
        with open(infile, 'rb') as f:
            f.seek(datastart)
            d = np.fromfile(f, dtype=np.float64).reshape((96, 37, -1), order='F')
            return d[:48, :, ::2]


        #The new HK format supports up to 96 hours and packs
        # zeros into unused positions
        data = data.reshape(96, 37, -1, order='F')
        nseasons = data.shape[-1] / 2
        return data[:48,:,:nseasons]

def createchangecards(header, parameters, outfile, outdir, albstr='a',
                      inertiastr='sk', taustr='t', log_inertias=True,
                      log='changecards.lis'):

    """
    Given a KRC header (an example is in examples/KRC/krc_header.py directory), 
    generate change cards for all parameter combinations in the parameters dict 
    (an example is in examples/KRC/parameters.config). These change cards are designed
    to run in parallel and are automatically chunked into some number of concurrently
    executable jobs.  Therefore, change cards are named with `outfile` prepended to 
    `outfile`_elevationname_chunknumber.inp. The files must declare where the resultant
    krc model runs will be written, then is controlled by the outdir argument.

    Parameters
    ----------

    header : str
             The KRC header with {} substitutions for version number, FLAY,
             K4OUT, elev

    parameters : dict
                 Keyed with 'inertia', 'tau', 'elevation', 'emissivity',
                 'slope_azimuth', and 'slope'. Each value, save 'inertia',
                 should be a list of the desired nodes.  Inertia should
                 be a start value, a stop value, and a number of steps.

    outfile : str
              The outfile name to be prepended to the change cards.

    outdir : str
             The PATH where the KRC model should write the output.

    albstr : str
             The character(s) used to prepend albedo in the model output filename. Default: 'a'

    inertiastr : str
                 The character(s) used to prepend inertia in the model output filename. Default: 'sk'

    taustr : str
             The character(s) used to prepend  tau in the model output filename. Default: 't'

    log_inertias : bool
                   If True, compute the log inertia vector (i.e, the inertias in the parameters are not
                   provided in log space.) Default: True
    
    log : str
          The PATH (filename) where a log of the generated change cards will be output.
    """

    # Parse albedo
    nalb = len(parameters['albedo'])
    albs = [i for i in parameters['albedo']]

    # Parse the inertia into an exponential range
    if log_inertias:
        ninertia = parameters['inertia'][2]
        inertias = compute_log_values(parameters['inertia'][0],
                                      parameters['inertia'][1],
                                      parameters['inertia'][2]).tolist()
    else:
        inertias = parameters['inertia']
        ninertia = len(inertias)

    # Parse Tau
    tau = parameters['tau']
    ntau = len(tau)
    taus = [i for i in tau]

    # Parse elevations
    elev = parameters['elevation']
    nelev = len(elev)
    elevstr = [i for i in elev]

    # Parse emissivity
    emissivity = parameters['emissivity']
    nemiss = len(emissivity)
    emissivities = [i for i in emissivity]

    # Parse SlopeAZ
    slopeaz = parameters['slope_azimuth']
    nslopeaz = len(slopeaz)
    slopeazs = [i for i in slopeaz]

    # Parse Slopes
    slope = parameters['slope']
    nslope = len(slope)
    slopes = [i for i in slope]

    # Get the output ext and the output directory
    ext = '.tds'

    parameters = list(itertools.product(
        inertias, albs, taus, emissivities, slopeazs, slopes))
    chunksize = int(len(parameters) / 5)
    chunks = [parameters[x:x + chunksize]
              for x in range(0, len(parameters), chunksize)]

    file_names = []
    # Loop over the elevations
    for e, elevation in enumerate(elev):
        elevationstr = """"""
        for j, l in enumerate([10, 10, 10, 7]):
            elevations = [elevation for v in range(l)]
            if j != 3:
                elevationstr += ''.join(str(w).rjust(7)
                                        for w in elevations) + '\n'
            else:
                elevationstr += ''.join(str(w).rjust(7) for w in elevations)

        for fnum, chunk in enumerate(chunks):
            ename = elev[e]
            if ename < 0:
                ename = 'n{}'.format(abs(ename))
            cfile = '{}_{}_{}.inp'.format(outfile, ename, fnum)
            with open(cfile, 'w') as out:
                out.write(header.format(elevationstr))
                if elevation < 0:
                    elevstr = 'em'
                else:
                    elevstr = 'ep'
                fnameelev = elevstr + str(abs(int(elevation)))

                for c in chunk:
                    inertia = c[0]
                    albedo = c[1]
                    tau = c[2]
                    emiss = c[3]
                    slopeaz = c[4]
                    slope = c[5]

                    # Albedo
                    out.write("1 1 {} 'Albedo'\n".format(round(float(albedo), 2)))
                    fnamealbedo = albstr + "{0:03d}".format(int(albedo * 100))

                    # Tau
                    out.write("1 17 {} 'Tau dust'\n".format(round(float(tau), 2)))
                    fnametau = taustr + "{0:03d}".format(int(tau * 100))

                    # Emissivity
                    out.write("1 2 {} 'Emissivity'\n".format(
                        round(float(emiss), 2)))
                    fnameemis = 'es{0:03d}'.format(int(emiss * 100))

                    # Slope Az
                    out.write("1 24 {} 'Slope Azimuth'\n".format(
                        round(float(slopeaz), 2)))
                    fnameslopeaz = 'az{0:03d}'.format(int(slopeaz))

                    # Slope
                    out.write("1 23 {} 'Slope'\n".format(round(float(slope), 2)))
                    fnameslope = 'sl{0:03d}'.format(int(slope))

                    # Inertia
                    out.write("1 3 {} 'Inertia'\n".format(
                        round(float(inertia), 1)))
                    fnameinertia = inertiastr + "{0:04d}".format(int(inertia))

                    # Write out the file PATH
                    outpath = os.path.join(outdir, fnameinertia + fnamealbedo +
                                        fnametau + fnameemis + fnameelev + fnameslopeaz + fnameslope + ext)
                    file_names.append(outpath)
                    if len(outpath) > 90:
                        print("Error!  Total filename length (path + name) exceeds 90 characters (Fortran limitation)")
                        print("Please select a new path with less nesting.")
                        sys.exit()
                    out.write("8 21 0 '{}'\n".format(outpath))
                    out.write('0/\n')
                for i in range(3):
                    out.write('0/\n')
    with open(os.path.join(outdir, log), 'w') as f:
        for l in file_names:
            f.write(l + '\n')