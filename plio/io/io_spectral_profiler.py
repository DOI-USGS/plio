import os
import pandas as pd
import pvl
import numpy as np

from plio.utils.utils import find_in_dict

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

    def __init__(self, input_data, label=None, cleaned=True, qa_threshold=2000):
        """
        Read the .spc file, parse the label, and extract the spectra

        Parameters
        ----------

        input_data : string
                     The PATH to the input .spc file

        label : string
                The PATH to an optional detached label associated with the .spc

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

        if label:
            label = pvl.load(label)
        else:
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
            try:
                ancillary_data_offset = find_in_dict(self.label, "^ANCILLARY_AND_SUPPLEMENT_DATA").value
            except:
                ancillary_data_offset = find_in_dict(self.label, "^ANCILLARY_AND_SUPPLEMENT_DATA")[1].value
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
            d = np.frombuffer(indata.read(rowbytes * nrows), dtype=rowdtype,
                              count=nrows)
            self.ancillary_data = pd.DataFrame(d, columns=columns,
                                               index=np.arange(nrows))
            keys = []
            vals = []
            for k, v in label.items():
                if k in ["ANCILLARY_AND_SUPPLEMENT_DATA", "L2D_RESULT_ARRAY",
                         "SP_SPECTRUM_QA", "SP_SPECTRUM_REF1", "SP_SPECTRUM_RAD",
                         "SP_SPECTRUM_REF2", "SP_SPECTRUM_RAW", "SP_SPECTRUM_WAV",
                         "^ANCILLARY_AND_SUPPLEMENT_DATA", "^SP_SPECTRUM_WAV",
                         "^SP_SPECTRUM_RAW", "^SP_SPECTRUM_REF2"," ^SP_SPECTRUM_RAD",
                         "^SP_SPECTRUM_REF1", "^SP_SPECTRUM_QA", "^L2D_RESULT_ARRAY",
                         "^SP_SPECTRUM_RAD"]:
                    continue
                if isinstance(v, pvl.collections.Quantity):
                    k = "{}_{}".format(k, v.units)
                    v = v.value
                keys.append(k)
                vals.append(v)

            vals = [vals] * len(self.ancillary_data)
            new_anc = pd.DataFrame(vals, index=self.ancillary_data.index, columns=keys)
            self.ancillary_data = self.ancillary_data.join(new_anc, how='inner')
            assert(ncols == len(columns))

            keys = []
            array_offsets = []
            for d in ['WAV', 'RAW', 'REF', 'REF1', 'REF2', 'DAR', 'QA', 'RAD']:
                search_key = '^SP_SPECTRUM_{}'.format(d)
                result = find_in_dict(label, search_key)
                if result:
                    try:
                        array_offsets.append(result.value)
                    except:
                        array_offsets.append(result[1].value) # 2C V3.0
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

                arr = np.frombuffer(indata.read(lines * 296*2), dtype='>H').astype(np.float64)
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
                    mask = self.spectra[i]['QA'] < qa_threshold
                    self.spectra[i] = self.spectra[i][mask]
            # If the spectra have been cleaned, the wavelength ids also need to be cleaned.
            if cleaned:
                self.wavelengths = self.wavelengths[mask.values].values

            dfs = [v for k, v in self.spectra.items()]
            self.spectra = pd.concat(dfs, axis=1, keys=range(nrows))

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

        from plio.io.io_gdal import GeoDataset
        path, ext = os.path.splitext(self.input_data)
        self.browse = GeoDataset(path + extension)
