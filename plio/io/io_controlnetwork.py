from time import gmtime, strftime

import pandas as pd
import numpy as np
import pvl

from plio.io import ControlNetFileV0002_pb2 as cnf
from plio.utils.utils import xstr, find_in_dict

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

class IsisControlNetwork(pd.DataFrame):

    # normal properties
    _metadata = ['header']

    @property
    def _constructor(self):
        return IsisControlNetwork

def from_isis(path, remove_empty=True):

    # Now get ready to work with the binary
    with IsisStore(path, mode='rb') as store:
        df = store.read()

    return df

def to_isis(path, obj, serials, mode='wb', version=2,
            headerstartbyte=HEADERSTARTBYTE,
            networkid='None', targetname='None',
            description='None', username=DEFAULTUSERNAME,
            creation_date=None, modified_date=None,
            pointid_prefix=None, pointid_suffix=None):
    """

    Write an AutoCNET Candidate graph object to an ISIS3 compatible control
    network.

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

    pointid_prefix : str
                     Prefix to be added to the pointid.  If the prefix is 'foo_', pointids
                     will be in the form 'foo_1, foo_2, ..., foo_n'

    pointid_suffix : str
                     Suffix to tbe added to the point id.  If the suffix is '_bar', pointids
                     will be in the form '1_bar, 2_bar, ..., n_bar'.
    """
    with IsisStore(path, mode) as store:
        if not creation_date:
            creation_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if not modified_date:
            modified_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        point_messages, point_sizes = store.create_points(obj, serials, pointid_prefix, pointid_suffix)
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
        self.nmeasures = 0
        self.npoints = 0

        # Conversion from buffer types to Python types
        bt = {1: float,
              5: int,
              8: bool,
              9: str,
              11: None,
              14: None}
        self.header_attrs = [(i.name, bt[i.type]) for i in cnf._CONTROLNETFILEHEADERV0002.fields]
        self.point_attrs = [(i.name, bt[i.type]) for i in cnf._CONTROLPOINTFILEENTRYV0002.fields]
        self.measure_attrs = [(i.name, bt[i.type]) for i in cnf._CONTROLPOINTFILEENTRYV0002_MEASURE.fields]

        self._path = path
        if not mode:
            mode = 'a' # pragma: no cover
        self._mode = mode
        self._handle = None

        self._open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.close()

    def close(self):
        if self._handle is not None:
            self._handle.close()
        self._handle = None

    def _open(self):
        self._handle = open(self._path, self._mode)

    def read(self):
        """
        Given an ISIS store, read the underlying ISIS3 compatible control network and
        return an IsisControlNetwork dataframe.
        """
        pvl_header = pvl.load(self._path)
        header_start_byte = find_in_dict(pvl_header, 'HeaderStartByte')
        header_bytes = find_in_dict(pvl_header, 'HeaderBytes')
        point_start_byte = find_in_dict(pvl_header, 'PointsStartByte')
        version = find_in_dict(pvl_header, 'Version')

        if version == 2:
            point_attrs = [i for i in cnf._CONTROLPOINTFILEENTRYV0002.fields_by_name if i != 'measures']
            measure_attrs = [i for i in cnf._CONTROLPOINTFILEENTRYV0002_MEASURE.fields_by_name]

        cols = point_attrs + measure_attrs

        cp = cnf.ControlPointFileEntryV0002()
        self._handle.seek(header_start_byte)
        pbuf_header = cnf.ControlNetFileHeaderV0002()
        pbuf_header.ParseFromString(self._handle.read(header_bytes))

        self._handle.seek(point_start_byte)
        cp = cnf.ControlPointFileEntryV0002()
        pts = []
        for s in pbuf_header.pointMessageSizes:
            cp.ParseFromString(self._handle.read(s))
            pt = [getattr(cp, i) for i in point_attrs if i != 'measures']

            for measure in cp.measures:
                meas = pt + [getattr(measure, j) for j in measure_attrs]
                pts.append(meas)
        df = IsisControlNetwork(pts, columns=cols)
        df.header = pvl_header
        return df


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

    def create_points(self, df, serials, pointid_prefix, pointid_suffix):
        """
        Step through a control network (C) and return protocol buffer point objects

        Parameters
        ----------
        df : DataFrame
              with the appropriate attributes: point_id, point_type, serial,
              measure_type, x, y required.
              The entries in the list must support grouping by the point_id attribute.

        Returns
        -------
        point_messages : list
                         of serialized points buffers

        point_sizes : list
                      of integer point sizes
        """
        def _set_pid(pointid):
            return '{}{}{}'.format(xstr(pointid_prefix),
                                   pointid,
                                   xstr(pointid_suffix))

        # TODO: Rewrite using apply syntax for performance
        point_sizes = []
        point_messages = []
        for i, g in df.groupby('point_id'):

            # Get the point specification from the protobuf
            point_spec = cnf.ControlPointFileEntryV0002()

            # Set the ID and then loop over all of the attributes that the
            # point has and check for corresponding columns in the group and
            # set with the correct type
            #point_spec.id = _set_pid(i)
            point_spec.id = _set_pid(i)
            for attr, attrtype in self.point_attrs:
                if attr in g.columns:
                    # As per protobuf docs for assigning to a repeated field.
                    if attr == 'aprioriCovar':
                        arr = g.iloc[0]['aprioriCovar']
                        if isinstance(arr, np.ndarray):
                            arr = arr.ravel().tolist()

                        point_spec.aprioriCovar.extend(arr)
                    else:
                        setattr(point_spec, attr, attrtype(g.iloc[0][attr]))
            point_spec.type = 2  # Hardcoded to free this is bad

            # The reference index should always be the image with the lowest index
            point_spec.referenceIndex = 0
            # A single extend call is cheaper than many add calls to pack points
            measure_iterable = []
            for node_id, m in g.iterrows():
                measure_spec = point_spec.Measure()
                # For all of the attributes, set if they are an dict accessible attr of the obj.
                for attr, attrtype in self.measure_attrs:
                    if attr in g.columns:
                        setattr(measure_spec, attr, attrtype(m[attr]))
                measure_spec.serialnumber = serials[m.image_index]
                measure_spec.sample = m.x
                measure_spec.line = m.y
                measure_spec.type = 2
                measure_iterable.append(measure_spec)
                self.nmeasures += 1

            self.npoints += 1

            point_spec.measures.extend(measure_iterable)
            point_message = point_spec.SerializeToString()
            point_sizes.append(point_spec.ByteSize())
            point_messages.append(point_message)
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
                        ('NumberOfPoints', self.npoints),
                        ('NumberOfMeasures', self.nmeasures),
                        ('Version', version)
                        ])
                  }),

                 )
        ])

        return pvl.dumps(header, cls=encoder)
