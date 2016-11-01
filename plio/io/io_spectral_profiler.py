import os
import pandas as pd
import pvl
import numpy as np

from plio.utils.utils import find_in_dict
from plio.io.io_gdal import GeoDataset

class Spectral_Profiler(object):

    """
    Attributes
    ----------

    spectra : panel
              A pandas panel containing n individual spectra.

    ancillary_data : dataframe
                     A pandas DataFrame of the parsed ancillary data (PVL label)

    label : object
            The raw PVL label object

    offsets : dict
              with key as the spectra index and value as the start byte offset
    """

    def __init__(self, input_data, cleaned=True, qa_threshold=2000):
        """
        Read the .spc file, parse the label, and extract the spectra

        Parameters
        ----------

        input_data : string
                     The PATH to the input .spc file

        cleaned : boolean
                  If True, mask the data based on the QA array.

        nspectra : int
                   The number of spectra in the given data file

        qa_threshold : int
                       The threshold value over which observations are masked as noise
                       if cleaned is True.
        """

        label_dtype_map = {'IEEE_REAL':'f',
                        'MSB_INTEGER':'i',
                        'MSB_UNSIGNED_INTEGER':'u'}


        label = pvl.load(input_data)
        self.label = label
        self.input_data = input_data
        with open(input_data, 'rb') as indata:
            # Extract and handle the ancillary data
            ancillary_data = find_in_dict(label, "ANCILLARY_AND_SUPPLEMENT_DATA")
            self.nspectra = nrows = ancillary_data['ROWS']
            ncols = ancillary_data['COLUMNS']
            rowbytes = ancillary_data['ROW_BYTES']

            columns = []
            bytelengths = []
            datatypes = []
            ancillary_data_offset = find_in_dict(label, "^ANCILLARY_AND_SUPPLEMENT_DATA").value
            indata.seek(ancillary_data_offset - 1)
            for i in ancillary_data.items():
                if i[0] == 'COLUMN':
                    entry = i[1]
                    # Level 2B2 PVL has entries with 0 bytes, e.g. omitted.
                    if entry['BYTES'] > 0:
                        columns.append(str(entry['NAME']))
                        datatypes.append(label_dtype_map[entry['DATA_TYPE']])
                        bytelengths.append(entry['BYTES'])
                    else:
                        ncols -= 1
            strbytes = map(str, bytelengths)
            rowdtype = list(zip(columns, map(''.join, zip(['>'] * ncols, datatypes, strbytes))))
            d = np.fromstring(indata.read(rowbytes * nrows), dtype=rowdtype,
                              count=nrows)
            self.ancillary_data = pd.DataFrame(d, columns=columns,
                                               index=np.arange(nrows))

            assert(ncols == len(columns))

            keys = []
            array_offsets = []
            for d in ['WAV', 'RAW', 'REF', 'REF1', 'REF2', 'DAR', 'QA']:
                search_key = '^SP_SPECTRUM_{}'.format(d)
                result = find_in_dict(label, search_key)
                if result:
                    array_offsets.append(result.value)
                    keys.append('SP_SPECTRUM_{}'.format(d))

            offsets = dict(zip(keys, array_offsets))

            arrays = {}
            for k, offset in offsets.items():
                indata.seek(offset - 1)
                newk = k.split('_')[-1]

                d = find_in_dict(label, k)
                unit = d['UNIT']
                lines = d['LINES']
                scaling_factor = d['SCALING_FACTOR']

                arr = np.fromstring(indata.read(lines * 296*2), dtype='>H').astype(np.float64)
                arr = arr.reshape(lines, -1)

                # If the data is scaled, apply the scaling factor
                if isinstance(scaling_factor, float):
                    arr *= scaling_factor

                arrays[newk] = arr

            self.wavelengths = pd.Series(arrays['WAV'][0])

            self.spectra = {}
            for i in range(nrows):
                self.spectra[i] = pd.DataFrame(index=self.wavelengths)
                for k in keys:
                    k = k.split('_')[-1]
                    if k == 'WAV':
                        continue
                    self.spectra[i][k] = arrays[k][i]

                if cleaned:
                    self.spectra[i] = self.spectra[i][self.spectra[i]['QA'] < qa_threshold]

            self.spectra = pd.Panel(self.spectra)

    def open_browse(self, extension='.jpg'):
        """
        Attempt to open the browse image corresponding to the spc file

        Parameters
        ----------
        extension : str
                    The file type extension to be added to the base name
                    of the spc file.

        Returns
        -------

        """
        path, ext = os.path.splitext(self.input_data)
        self.browse = GeoDataset(path + extension)
