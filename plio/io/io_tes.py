import numpy as np
import pandas as pd
import pvl

import sys
import functools
import json

from plio.io.io_json import read_json

from plio.io import tes_dtype_map
from plio.io import tes_columns
from plio.io import tes_scaling_factors

class Tes(object):
    """
    Attributes
    ----------

    spectra : panel
              A pandas panel containing n individual spectra.

    ancillary_data : dataframe
                     A pandas DataFrame of the parsed ancillary data (PVL label)

    label : object
            The raw PVL label object

    """

    def __init__(self, input_data, var_file = None):
        """
        Read the .spc file, parse the label, and extract the spectra

        Parameters
        ----------

        input_data : string
                     The PATH to the input .tab file

        """
        def expand_column(df, expand_column, columns):
            array = np.asarray([np.asarray(list(tup[0])) for tup in df[expand_column].as_matrix()], dtype=np.uint8)
            new_df = pd.concat([df, pd.DataFrame(array, columns=columns)], axis=1)
            del new_df[expand_column]
            return new_df

        def bolquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bit2bool(bitarr[3:4]))]

            types = [('BOLOMETRIC_INERTIA_RATING', '>u1'), ('BOLOMETER_LAMP_ANOMALY', 'bool_')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:5]),
                    bitarr2int(bitarr[5:6]), bitarr2int(bitarr[6:7]),
                    bitarr2int(bitarr[7:8]), bitarr2int(bitarr[8:9]))]

            types = [('HGA_MOTION', '>u1'), ('SOLAR_PANEL_MOTION', '>u1'), ('ALGOR_PATCH', '>u1'),
                     ('IMC_PATCH', '>u1'), ('MOMENTUM_DESATURATION', '>u1'), ('EQUALIZATION_TABLE', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsclass2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bitarr2int(bitarr[3:7]),
                    bitarr2int(bitarr[7:11]), bitarr2int(bitarr[11:13]),
                    bitarr2int(bitarr[13:14]), bitarr2int(bitarr[14:16]),
                    bitarr2int(bitarr[16:]))]

            types = [('MISSION_PHASE', '>u1'), ('INTENDED_TARGET', '>u1'), ('TES_SEQUENCE', '>u1'),
                     ('NEON_LAMP_STATUS', '>u1'), ('TIMING_ACCURACY', '>u1'), ('SPARE', '>u1'), ('CLASSIFICATION_VALUE', '>u2')]
            arr = np.array(lis, dtype=types)
            return arr

        def radquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:1]), bitarr2int(bitarr[1:2]),
                    bitarr2int(bitarr[2:3]), bitarr2int(bitarr[3:5]),
                    bitarr2int(bitarr[5:7]), bitarr2int(bitarr[5:8]),
                    bitarr2int(bitarr[8:9]))]

            types = [('MAJOR_PHASE_INVERSION', '>u1'), ('ALGOR_RISK', '>u1'), ('CALIBRATION_FAILURE', '>u1'),
                     ('CALIBRATION_QUALITY', '>u1'), ('SPECTROMETER_NOISE', '>u1'), ('SPECTRAL_INERTIA_RATING', '>u1'),
                     ('DETECTOR_MASK_PROBLEM', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def atmquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:4]))]

            types = [('TEMPERATURE_PROFILE_RATING', '>u1'), ('ATMOSPHERIC_OPACITY_RATING', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def expand_column(df, expand_column, columns):
            array = np.asarray([np.asarray(list(tup[0])) for tup in df[expand_column].as_matrix()], dtype=np.uint8)
            new_df = pd.concat([df, pd.DataFrame(array, columns=columns)], axis=1)
            del new_df[expand_column]
            return new_df

        def bolquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bit2bool(bitarr[3:4]))]

            types = [('BOLOMETRIC_INERTIA_RATING', '>u1'), ('BOLOMETER_LAMP_ANOMALY', 'bool_')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:5]),
                    bitarr2int(bitarr[5:6]), bitarr2int(bitarr[6:7]),
                    bitarr2int(bitarr[7:8]), bitarr2int(bitarr[8:9]))]

            types = [('HGA_MOTION', '>u1'), ('SOLAR_PANEL_MOTION', '>u1'), ('ALGOR_PATCH', '>u1'),
                     ('IMC_PATCH', '>u1'), ('MOMENTUM_DESATURATION', '>u1'), ('EQUALIZATION_TABLE', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsclass2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bitarr2int(bitarr[3:7]),
                    bitarr2int(bitarr[7:11]), bitarr2int(bitarr[11:13]),
                    bitarr2int(bitarr[13:14]), bitarr2int(bitarr[14:16]),
                    bitarr2int(bitarr[16:]))]

            types = [('MISSION_PHASE', '>u1'), ('INTENDED_TARGET', '>u1'), ('TES_SEQUENCE', '>u1'),
                     ('NEON_LAMP_STATUS', '>u1'), ('TIMING_ACCURACY', '>u1'), ('SPARE', '>u1'), ('CLASSIFICATION_VALUE', '>u2')]
            arr = np.array(lis, dtype=types)
            return arr

        def radquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:1]), bitarr2int(bitarr[1:2]),
                    bitarr2int(bitarr[2:3]), bitarr2int(bitarr[3:5]),
                    bitarr2int(bitarr[5:7]), bitarr2int(bitarr[5:8]),
                    bitarr2int(bitarr[8:9]))]

            types = [('MAJOR_PHASE_INVERSION', '>u1'), ('ALGOR_RISK', '>u1'), ('CALIBRATION_FAILURE', '>u1'),
                     ('CALIBRATION_QUALITY', '>u1'), ('SPECTROMETER_NOISE', '>u1'), ('SPECTRAL_INERTIA_RATING', '>u1'),
                     ('DETECTOR_MASK_PROBLEM', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def atmquality2arr(arr):
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:4]))]

            types = [('TEMPERATURE_PROFILE_RATING', '>u1'), ('ATMOSPHERIC_OPACITY_RATING', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def tes2numpy(msb_type, num_bytes, nelems=1):
            """
            Converts a MSB data type to a numpy datatype

            """
            valid_bytes = {
                'MSB_UNSIGNED_INTEGER': [1,2,4,8,16,32,64],
                'MSB_INTEGER': [1,2,4,8,16,32,64],
                'IEEE_REAL': [1,2,4,8,16,32,64],
                'CHARACTER': range(1,128),
                'MSB_BIT_STRING': range(1,128)
            }

            msb_bit_string_type = [('byte{}'.format(i), '>u1') for i in range(num_bytes)]

            dtype_map = {
                'MSB_UNSIGNED_INTEGER': '>u{}'.format(num_bytes),
                'MSB_INTEGER': '>i{}'.format(num_bytes),
                'IEEE_REAL': '>f{}'.format(num_bytes),
                'CHARACTER': 'a{}'.format(num_bytes),
                'MSB_BIT_STRING': msb_bit_string_type
            }

            if num_bytes not in valid_bytes[msb_type] and not nelems:
                raise Exception('invalid byte ({}) count for type ({})'.format(num_bytes, msb_type))

            if nelems > 1:
                # Must be an array
                return [('elem{}'.format(i), dtype_map[msb_type]) for i in range(nelems)]


            return dtype_map[msb_type]

        def bitarr2int(arr):
            arr = "".join(str(i) for i in arr)
            return np.uint8(int(arr,2))

        def bit2bool(bit):
            return np.bool_(bit)

        def expand_bitstrings(df, dataset):
            if dataset == 'BOL':
                quality_columns = ['ti_bol_rating', 'bol_ref_lamp']
                df['quality'] = df['quality'].apply(bolquality2arr)
                return expand_column(df, 'quality', quality_columns)

            elif dataset == 'OBS':
                quality_columns = ['hga_motion', 'pnl_motion', 'algor_patch', 'imc_patch',
                                   'momentum', 'equal_tab']
                class_columns = ['phase', 'type', 'sequence',
                                 'lamp_status', 'timing', 'spare', 'class_value']

                df['quality'] = df['quality'].apply(obsquality2arr)
                df['class'] = df['class'].apply(obsclass2arr)

                new_df = expand_column(df, 'quality', quality_columns)
                new_df = expand_column(new_df, 'class', class_columns)
                return new_df

            elif dataset == 'RAD':
                quality_columns = ['phase_inversion', 'algor_risk', 'calib_fail', 'calib_quality',
                                   'spect_noise', 'ti_spc_rating', 'det_mask_problem']

                df['quality'] = df['quality'].apply(radquality2arr)

                return expand_column(df, 'quality', quality_columns)

            elif dataset == 'ATM':
                quality_columns = ['atm_pt_rating', 'atm_opacity_rating']

                df['quality'] = df['quality'].apply(atmquality2arr)
                return expand_column(df, 'quality', quality_columns)

            else:
                return df

        self.label = pvl.load(input_data)
        nrecords = self.label['TABLE']['ROWS']
        nbytes_per_rec = self.label['RECORD_BYTES']
        data_start = self.label['LABEL_RECORDS'] * self.label['RECORD_BYTES']
        dataset = self.label['TABLE']['^STRUCTURE'].split('.')[0]

        numpy_dtypes = tes_dtype_map
        columns = tes_columns
        scaling_factors = tes_scaling_factors

        with open(input_data, 'rb') as file:
            file.seek(data_start)
            buffer = file.read(nrecords*nbytes_per_rec)
            array = np.frombuffer(buffer, dtype=numpy_dtypes[dataset.upper()]).byteswap().newbyteorder()

        df = pd.DataFrame(data=array, columns=columns[dataset.upper()])

        # Read Radiance array if applicable
        if dataset.upper() == 'RAD':
            with open('{}.var'.format(path.splitext(f)[0]) , 'rb') as file:
                buffer = file.read()
                def process_rad(index):
                    if index is -1:
                        return None

                    length = np.frombuffer(buffer[index:index+2], dtype='>u2')[0]
                    exp = np.frombuffer(buffer[index+2:index+4], dtype='>i2')[0]

                    radarr = np.frombuffer(buffer[index+4:index+4+length-2], dtype='>i2') * (2**(exp-15))
                    if np.frombuffer(buffer[index+4+length-2:index+4+length], dtype='>u2')[0] != length:
                        warnings.warn("Last element did not match the length for file index {} in file {}".format(index, f))
                    return radarr

                df["raw_rad"] = df["raw_rad"].apply(process_rad)
                df["cal_rad"] = df["cal_rad"].apply(process_rad)

        # Apply scaling factors
        for column in scaling_factors[dataset]:
            def scale(x):
                 return np.multiply(x, scaling_factors[dataset][column])
            df[column] = df[column].apply(scale)

        df =  expand_bitstrings(df, dataset.upper())

        self.data =  df
