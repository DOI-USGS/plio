import numpy as np
import pandas as pd
import pvl

import sys
import functools
import json

from os import path
from plio.io.io_json import read_json
from plio.utils._tes2numpy import tes_dtype_map
from plio.utils._tes2numpy import tes_columns
from plio.utils._tes2numpy import tes_scaling_factors

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


    def __init__(self, input_data, var_file = None, data_set=None):
        """
        Read the .spc file, parse the label, and extract the spectra

        Parameters
        ----------

        input_data : string
                     The PATH to the input .tab file

        """
        def expand_column(df, expand_column, columns): # pragma: no cover
            array = np.asarray([np.asarray(list(tup[0])) for tup in df[expand_column].as_matrix()], dtype=np.uint8)
            new_df = pd.concat([df, pd.DataFrame(array, columns=columns)], axis=1)
            del new_df[expand_column]
            return new_df

        def bolquality2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bit2bool(bitarr[3:4]))]

            types = [('BOLOMETRIC_INERTIA_RATING', '>u1'), ('BOLOMETER_LAMP_ANOMALY', 'bool_')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsquality2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:5]),
                    bitarr2int(bitarr[5:6]), bitarr2int(bitarr[6:7]),
                    bitarr2int(bitarr[7:8]), bitarr2int(bitarr[8:9]))]

            types = [('HGA_MOTION', '>u1'), ('SOLAR_PANEL_MOTION', '>u1'), ('ALGOR_PATCH', '>u1'),
                     ('IMC_PATCH', '>u1'), ('MOMENTUM_DESATURATION', '>u1'), ('EQUALIZATION_TABLE', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsclass2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bitarr2int(bitarr[3:7]),
                    bitarr2int(bitarr[7:11]), bitarr2int(bitarr[11:13]),
                    bitarr2int(bitarr[13:14]), bitarr2int(bitarr[14:16]),
                    bitarr2int(bitarr[16:]))]

            types = [('MISSION_PHASE', '>u1'), ('INTENDED_TARGET', '>u1'), ('TES_SEQUENCE', '>u1'),
                     ('NEON_LAMP_STATUS', '>u1'), ('TIMING_ACCURACY', '>u1'), ('SPARE', '>u1'), ('CLASSIFICATION_VALUE', '>u2')]
            arr = np.array(lis, dtype=types)
            return arr

        def radquality2arr(arr): # pragma: no cover
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

        def atmquality2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:4]))]

            types = [('TEMPERATURE_PROFILE_RATING', '>u1'), ('ATMOSPHERIC_OPACITY_RATING', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def expand_column(df, expand_column, columns): # pragma: no cover
            array = np.asarray([np.asarray(list(tup[0])) for tup in df[expand_column].as_matrix()], dtype=np.uint8)
            new_df = pd.concat([df, pd.DataFrame(array, columns=columns)], axis=1)
            del new_df[expand_column]
            return new_df

        def bolquality2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bit2bool(bitarr[3:4]))]

            types = [('BOLOMETRIC_INERTIA_RATING', '>u1'), ('BOLOMETER_LAMP_ANOMALY', 'bool_')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsquality2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:5]),
                    bitarr2int(bitarr[5:6]), bitarr2int(bitarr[6:7]),
                    bitarr2int(bitarr[7:8]), bitarr2int(bitarr[8:9]))]

            types = [('HGA_MOTION', '>u1'), ('SOLAR_PANEL_MOTION', '>u1'), ('ALGOR_PATCH', '>u1'),
                     ('IMC_PATCH', '>u1'), ('MOMENTUM_DESATURATION', '>u1'), ('EQUALIZATION_TABLE', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def obsclass2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:3]), bitarr2int(bitarr[3:7]),
                    bitarr2int(bitarr[7:11]), bitarr2int(bitarr[11:13]),
                    bitarr2int(bitarr[13:14]), bitarr2int(bitarr[14:16]),
                    bitarr2int(bitarr[16:]))]

            types = [('MISSION_PHASE', '>u1'), ('INTENDED_TARGET', '>u1'), ('TES_SEQUENCE', '>u1'),
                     ('NEON_LAMP_STATUS', '>u1'), ('TIMING_ACCURACY', '>u1'), ('SPARE', '>u1'), ('CLASSIFICATION_VALUE', '>u2')]
            arr = np.array(lis, dtype=types)
            return arr

        def radquality2arr(arr): # pragma: no cover
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

        def atmquality2arr(arr): # pragma: no cover
            bitarr = np.unpackbits(np.asarray(arr, dtype=np.uint8))
            lis = [(bitarr2int(bitarr[0:2]), bitarr2int(bitarr[2:4]))]

            types = [('TEMPERATURE_PROFILE_RATING', '>u1'), ('ATMOSPHERIC_OPACITY_RATING', '>u1')]
            arr = np.array(lis, dtype=types)
            return arr

        def bitarr2int(arr): # pragma: no cover
            arr = "".join(str(i) for i in arr)
            return np.uint8(int(arr,2))

        def bit2bool(bit): # pragma: no cover
            return np.bool_(bit)

        def expand_bitstrings(df, dataset): # pragma: no cover
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

        if isinstance(input_data, pd.DataFrame):
            self.dataset = None
            if not data_set:
                for key in tes_columns.keys():
                    if len(set(tes_columns[key]).intersection(set(input_data.columns))) > 3 :
                        self.dataset = key
            else:
                self.dataset=data_set

            self.label = None
            self.data = input_data
            return

        self.label = pvl.load(input_data)
        nrecords = self.label['TABLE']['ROWS']
        nbytes_per_rec = self.label['RECORD_BYTES']
        data_start = self.label['LABEL_RECORDS'] * self.label['RECORD_BYTES']
        dataset = self.label['TABLE']['^STRUCTURE'].split('.')[0]
        self.dataset = dataset

        numpy_dtypes = tes_dtype_map
        columns = tes_columns
        scaling_factors = tes_scaling_factors

        with open(input_data, 'rb') as file:
            file.seek(data_start)
            buffer = file.read(nrecords*nbytes_per_rec)
            array = np.frombuffer(buffer, dtype=numpy_dtypes[dataset.upper()]).byteswap().newbyteorder()

        df = pd.DataFrame(data=array, columns=columns[dataset.upper()])

        # Read Radiance array if applicable
        if dataset.upper() == 'RAD': # pragma: no cover
            if not var_file:
                filename, file_extension = path.splitext(input_data)
                var_file = filename + ".var"

            with open(var_file, "rb") as var:
                buffer = var.read()
                def process_rad(index):
                    if index == -1:
                        return None

                    length = np.frombuffer(buffer[index:index+2], dtype='>u2')[0]
                    exp = np.frombuffer(buffer[index+2:index+4], dtype='>i2')[0]
                    scale = 2**(int(exp)-15)
                    radarr = np.frombuffer(buffer[index+4:index+4+length-2], dtype='>i2') * scale
                    if np.frombuffer(buffer[index+4+length-2:index+4+length], dtype='>u2')[0] != length:
                        warnings.warn("Last element did not match the length for file index {} in file {}".format(index, f))
                    return radarr

                df["raw_rad"] = df["raw_rad"].apply(process_rad)
                df["cal_rad"] = df["cal_rad"].apply(process_rad)

        # Apply scaling factors
        for column in scaling_factors[dataset]: # pragma: no cover
            def scale(x):
                 return np.multiply(x, scaling_factors[dataset][column])
            df[column] = df[column].apply(scale)

        df =  expand_bitstrings(df, dataset.upper())

        self.data =  df

    def join(tes_data):
        """
        Given a list of Tes objects, merges them into a single dataframe using
        SPACECRAFT_CLOCK_START_COUNT (sclk_time) as the index.

        Parameters
        ----------

        tes_data : iterable
                   A Python iterable of Tes objects

        Returns
        -------

        : dataframe
          A pandas dataframe containing the merged data

        : outliers
          A list of Tes() objects containing the tables containing no matches
        """
        if not hasattr(tes_data, '__iter__') and not isinstance(tes_data, Tes):
            raise TypeError("Input data must be a Tes datasets or an iterable of Tes datasets, got {}".format(type(tes_data)))
        elif not hasattr(tes_data, '__iter__'):
            tes_data = [tes_data]

        if len(tes_data) == 0:
            warn("Input iterable is empty")

        if not all([isinstance(obj, Tes) for obj in tes_data]):
            # Get the list of types and the indices of elements that caused the error
            types = [type(obj) for obj in tes_data]
            error_idx = [i for i, x in enumerate([isinstance(obj, Tes) for obj in tes_data]) if x == False]

            raise TypeError("Input data must must be a Tes dataset, input array has non Tes objects at indices: {}\
                             for inputs of type: {}".format(error_idx, types))

        single_key_sets = {'ATM', 'POS', 'TLM', 'OBS'}
        compound_key_sets = {'BOL', 'CMP', 'GEO', 'IFG', 'PCT', 'RAD'}
        dfs = dict.fromkeys(single_key_sets | compound_key_sets, DataFrame())

        # Organize the data based on datasets
        for ds in tes_data:
            # Find a way to do this in place?
            dfs[ds.dataset] = dfs[ds.dataset].append(ds.data)

        # remove and dataframes that are empty
        empty_dfs = [key for key in dfs.keys() if dfs[key].empty]
        for key in empty_dfs:
            dfs.pop(key, None)


        single_key_dfs = [dfs[key] for key in dfs.keys() if key in single_key_sets]
        compound_key_dfs = [dfs[key] for key in dfs.keys() if key in compound_key_sets]
        all_dfs = single_key_dfs+compound_key_dfs

        keyspace = functools.reduce(lambda left,right: left|right, [set(df['sclk_time']) for df in all_dfs])

        single_key_merged = functools.reduce(lambda left,right: pd.merge(left, right, on=["sclk_time"]), single_key_dfs)
        compound_key_merged = functools.reduce(lambda left,right: pd.merge(left, right, on=["sclk_time", "detector"]), compound_key_dfs)
        merged = single_key_merged.merge(compound_key_merged, on="sclk_time")

        outlier_idx = keyspace-set(merged["sclk_time"])
        outliers = [Tes(tds.data[tds.data['sclk_time'].isin(outlier_idx)], data_set=tds.dataset) for tds in tes_data]
        return merged, [tds for tds in outliers if not tds.data.empty]
