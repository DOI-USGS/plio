from time import gmtime, strftime
import pvl

from plio import ControlNetFileV0002_pb2 as cnf

VERSION = 2
HEADERSTARTBYTE = 65536
DEFAULTUSERNAME = 'None'


def write_filelist(lst, path="fromlist.lis"):
    """
    Writes a filelist to a file so it can be used in ISIS3.

    Parameters
    ----------
    lst : list
          A list containing full paths to the images used, as strings.
    path : str
           The name of the file to write out. Default: fromlist.lis
    """
    handle = open(path, 'w')
    for filename in lst:
        handle.write(filename)
        handle.write('\n')
    return


def to_isis(path, obj, mode='w', version=VERSION,
            headerstartbyte=HEADERSTARTBYTE,
            networkid='None', targetname='None',
            description='None', username=DEFAULTUSERNAME,
            creation_date=None, modified_date=None):
    """
    Parameters
    ----------
    path : str
           Input path where the file is to be written

    network : dict
              A dict of lists keyed with a

    mode : {'a', 'w', 'r', 'r+'}

        ``'r'``
            Read-only; no data can be modified.
        ``'w'``
            Write; a new file is created (an existing file with the same
            name would be deleted).
        ``'a'``
            Append; an existing file is opened for reading and writing,
            and if the file does not exist it is created.
        ``'r+'``
            It is similar to ``'a'``, but the file must already exist.

    version : int
          The current ISIS version to write, defaults to 2

    headerstartbyte : int
                      The seek offset that the protocol buffer header starts at

    networkid : str
                The name of the network

    targetname : str
                 The name of the target, e.g. Moon

    description : str
                  A description for the network.

    username : str
               The name of the user / application that created the control network
    """

    with IsisStore(path, mode) as store:
        if not creation_date:
            creation_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if not modified_date:
            modified_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        point_messages, point_sizes = store.create_points(obj)
        points_bytes = sum(point_sizes)
        buffer_header, buffer_header_size = store.create_buffer_header(networkid,
                                                                       targetname,
                                                                       description,
                                                                       username,
                                                                       point_sizes,
                                                                       creation_date,
                                                                       modified_date)
        # Write the buffer header
        store.write(buffer_header, HEADERSTARTBYTE)
        # Then write the points, so we know where to start writing, + 1 to avoid overwrite
        point_start_offset = HEADERSTARTBYTE + buffer_header_size
        for i, point in enumerate(point_messages):
            store.write(point, point_start_offset)
            point_start_offset += point_sizes[i]

        header = store.create_pvl_header(version, headerstartbyte, networkid,
                                         targetname, description, username,
                                         buffer_header_size, points_bytes,
                                         creation_date, modified_date)


        store.write(header)


class IsisStore(object):
    """
    Class to manage IO of an ISIS control network (version 2).

    Attributes
    ----------
    pointid : int
              The current index to be assigned to newly added points
    """

    def __init__(self, path, mode=None, **kwargs):
        self.pointid = 0
        self.nmeasures = 0

        self._path = path
        if not mode:
            mode = 'a' # pragma: no cover
        self._mode = mode
        self._handle = None

        self._open()

    def _open(self):
        if self._mode in ['wb', 'a']:
            self._handle = open(self._path, self._mode)
        else:
            raise NotImplementedError

    def write(self, data, offset=0):
        """
        Parameters
        ----------
        data : str
               to be written to the file

        offset : int
                 The byte offset into the output binary
        """
        self._handle.seek(offset)
        self._handle.write(data)

    def create_points(self, obj):
        """
        Step through a control network (C) and return protocol buffer point objects

        Parameters
        ----------
        obj : list
              of iterable objects (dataframes) with the appropriate
              attributes: point_id, point_type, serial,  measure_type, x, y required.
              The entries in the list must support grouping by the point_id attribute.

        Returns
        -------
        point_messages : list
                         of serialized points buffers

        point_sizes : list
                      of integer point sizes
        """
        # TODO: Rewrite using apply syntax for performance
        point_sizes = []
        point_messages = []
        for df in obj:
            for i, g in df.groupby('point_id'):
                point_spec = cnf.ControlPointFileEntryV0002()
                point_spec.id = str(self.pointid)
                point_spec.type = int(g.point_type.iat[0])

                # The reference index should always be the image with the lowest index
                point_spec.referenceIndex = 0

                # A single extend call is cheaper than many add calls to pack points
                measure_iterable = []

                for node_id, m in g.iterrows():
                    measure_spec = point_spec.Measure()
                    try:
                        measure_spec.serialnumber = m.serialnumber
                    except:
                        measure_spec.serialnumber = str(m.serialnumber)
                    measure_spec.type = m.measure_type
                    measure_spec.sample = float(m.x)
                    measure_spec.line = float(m.y)

                    measure_iterable.append(measure_spec)
                    self.nmeasures += 1
                point_spec.measures.extend(measure_iterable)

                point_message = point_spec.SerializeToString()
                point_sizes.append(point_spec.ByteSize())
                point_messages.append(point_message)

                self.pointid += 1
        return point_messages, point_sizes

    def create_buffer_header(self, networkid, targetname,
                             description, username, point_sizes,
                             creation_date,
                             modified_date):
        """
        Create the Google Protocol Buffer header using the
        protobuf spec.

        Parameters
        ----------
        networkid : str
                    The user defined identifier of this control network

        targetname : str
                 The name of the target, e.g. Moon

        description : str
                  A description for the network.

        username : str
               The name of the user / application that created the control network

        point_sizes : list
                      of the point sizes for each point message

        Returns
        -------
        header_message : str
                  The serialized message to write

        header_message_size : int
                              The size of the serialized header, in bytes
        """
        raw_header_message = cnf.ControlNetFileHeaderV0002()
        raw_header_message.created = creation_date
        raw_header_message.lastModified = modified_date
        raw_header_message.networkId = networkid
        raw_header_message.description = description
        raw_header_message.targetName = targetname
        raw_header_message.userName = username
        raw_header_message.pointMessageSizes.extend(point_sizes)

        header_message_size = raw_header_message.ByteSize()
        header_message = raw_header_message.SerializeToString()

        return header_message, header_message_size

    def create_pvl_header(self, version, headerstartbyte,
                      networkid, targetname, description, username,
                          buffer_header_size, points_bytes,
                          creation_date, modified_date):
        """
        Create the PVL header object

        Parameters
        ----------
        version : int
              The current ISIS version to write, defaults to 2

        headerstartbyte : int
                          The seek offset that the protocol buffer header starts at

        networkid : str
                    The name of the network

        targetname : str
                     The name of the target, e.g. Moon

        description : str
                      A description for the network.

        username : str
                   The name of the user / application that created the control network

        buffer_header_size : int
                             Total size of the header in bytes

        points_bytes : int
                       The total number of bytes all points require

        Returns
        -------
         : object
           An ISIS compliant PVL header object

        """

        encoder = pvl.encoder.IsisCubeLabelEncoder

        header_bytes = buffer_header_size
        points_start_byte = HEADERSTARTBYTE + buffer_header_size

        header = pvl.PVLModule([
            ('ProtoBuffer',
                ({'Core':{'HeaderStartByte': headerstartbyte,
                        'HeaderBytes': header_bytes,
                        'PointsStartByte': points_start_byte,
                        'PointsBytes': points_bytes},

                  'ControlNetworkInfo': pvl.PVLGroup([
                        ('NetworkId', networkid),
                        ('TargetName', targetname),
                        ('UserName', username),
                        ('Created', creation_date),
                        ('LastModified', modified_date),
                        ('Description', description),
                        ('NumberOfPoints', self.pointid),
                        ('NumberOfMeasures', self.nmeasures),
                        ('Version', version)
                        ])
                  }),

                 )
        ])

        return pvl.dumps(header, cls=encoder)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.close()

    def close(self):
        if self._handle is not None:
            self._handle.close()
        self._handle = None


