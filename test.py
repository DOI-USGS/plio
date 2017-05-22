import sys
import os

import plio
from plio.io.io_tes import Tes

from glob import glob
from os import path

import functools
import pandas as pd
from pymongo import MongoClient
from warnings import warn
from collections import Iterable
import pandas as pd
from pandas import DataFrame

import functools
import json

def join_tes(tes_data, init_dfs=None):
    """


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
    outliers = [Tes(tds.data[tds.data['sclk_time'].isin(outlier_idx)]) for tds in tes_data]
    return merged, [tds for tds in outliers if not tds.data.empty]


def clamp_longitude(angle):
    """
    Returns the angle limited to the range [-180, 180], the original
    data is in the range [0,360] but mongo uses [-180,180].

    Parameters
    ----------
    angle : float
       The angle to clamp

    Returns
    -------
    : float
       The clamped angle
    """
    return ((angle + 180) % 360) - 180

def to_mongodb(chunk_size=60):
    data_dir = '/scratch/jlaura/tes/tes_data/'
    folders = [folder for folder in os.listdir(data_dir) if folder[:4] == "mgst"]

    search_len = len(data_dir) + 9
    print("search len: {}".format(search_len))

    folders = sorted(folders, key=lambda x:int(x[5:]))[4:]
    print("first 20 Folders:")
    print("\n".join(folders[:20]))

    num_files = len(glob(data_dir+'mgst_*/*.tab'))
    print("Number of files: {}".format(num_files))

    outliers = []
    client = MongoClient('localhost', 27017)
    print(client.server_info())

    db = client.tes
    processed = 0
    json_objs = []
    for folder in folders:
        files = glob(data_dir+folder+'/*.tab')
        length = len(files)
        print("On folder {} with {} files.".format(folder, len(files)))
        print("COMPLETE: {}/{} {}".format(processed, num_files, processed/num_files))
        tes_datasets = [Tes(file) for file in files] + outliers
        dfs, outliers = join_tes(tes_datasets)
        print("Num records: {}".format(dfs.shape[0]))
        print("Num outliers: {}".format(len(outliers)))
        try:
            json_objs = json.loads(dfs.to_json(orient='records'))

            del dfs
            print("Num json objs: {}".format(len(json_objs)))
            for dictionary in json_objs:
                dictionary["loc"] = {
                    "type" : "Point",
                    "coordinates" : [clamp_longitude(dictionary["longitude"]), dictionary["latitude"]]
                }

            db.point_data.insert_many(json_objs, bypass_document_validation=True)
        except Exception as e:
            print("Had exception during processing: {}".format(e))


        json_objs = None
        processed = processed + length
        print()

    



if __name__ == "__main__":
    to_mongodb()
