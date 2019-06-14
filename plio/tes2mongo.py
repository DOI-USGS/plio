import sys
import os

import argparse
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

import pytes
from pytes.utils.utils import mgs84_norm_lat
from pytes.utils.utils import mgs84_norm_long

total_folders = 326
total_files = 13393

def to_mongodb(data_dir, out_dir, sl, using_csv=False):
    if using_csv:
        files = glob(data_dir+"/**/*.csv")
        print("Number of Files: {}".format(len(files)))
        outliers = []
        client = MongoClient('130.118.160.193', 27017)

        try:
            client.server_info()
            print("Connection Successful!")
        except Exception as e:
            print("Failed to connect: {}".format(e))

        db = client.tes
        processed = 0
        tes_datasets = [Tes(file) for file in files]
        dfs, outliers = Tes.join(tes_datasets)

        print("Num records: {}".format(dfs.shape[0]))
        print("Num outliers: {}".format(len(outliers)))
        del outliers

        try:
            json_objs = json.loads(dfs.to_json(orient='records'))

            del dfs
            print("Num json objs: {}".format(len(json_objs)))
            for dictionary in json_objs:
                dictionary["loc"] = {
                    "type" : "Point",
                    "coordinates" : [mgs84_norm_long(dictionary["longitude"]), mgs84_norm_lat(dictionary["latitude"])]
                }

            db.point_data.insert_many(json_objs, bypass_document_validation=True)
        except Exception as e:
            print("Had exception during processing: {}".format(e))
        return

    folders = [folder for folder in os.listdir(data_dir) if folder[:4] == "mgst"]

    search_len = len(data_dir) + 9
    print("search len: {}".format(search_len))
    print("Slice: {}".format(sl))
    folders = sorted(folders, key=lambda x:int(x[5:]))[sl]
    print("Processing Folders: {} to {}".format(folders[0], folders[-1]))
    print("Number of folders: {}".format(len(folders)))
    num_files = len(glob(data_dir+'mgst_*/*.tab'))
    print("Number of files: {}".format(num_files))

    outliers = []
    client = MongoClient('130.118.160.193', 27017)

    try:
        client.server_info()
        print("Connection Successful!")
    except Exception as e:
        print("Failed to connect: {}".format(e))

    db = client.tes
    processed = 0
    for folder in folders:
        files = glob(data_dir+folder+'/*.tab')
        length = len(files)
        print("On folder {} with {} files.".format(folder, len(files)))
        print("COMPLETE: {}/{} {}".format(processed, num_files, processed/num_files))
        tes_datasets = [Tes(file) for file in files]
        dfs, outliers = Tes.join(tes_datasets)

        print("Num records: {}".format(dfs.shape[0]))
        print("Num outliers: {}".format(len(outliers)))

        single_key_sets = {'ATM', 'POS', 'TLM', 'OBS'}
        compound_key_sets = {'BOL', 'CMP', 'GEO', 'IFG', 'PCT', 'RAD'}
        counts = dict.fromkeys(single_key_sets | compound_key_sets,0)
        for tes in outliers:
            counts[tes.dataset] = counts[tes.dataset] + 1
            tes.data.to_csv(out_dir+"/"+folder+"_"+tes.dataset+str(counts[tes.dataset])+".csv")

        del outliers

        try:
            json_objs = json.loads(dfs.to_json(orient='records'))

            del dfs
            print("Num json objs: {}".format(len(json_objs)))
            for dictionary in json_objs:
                dictionary["loc"] = {
                    "type" : "Point",
                    "coordinates" : [mgs84_norm_long(dictionary["longitude"]), mgs84_norm_lat(dictionary["latitude"])]
                }

            db.point_data.insert_many(json_objs, bypass_document_validation=True)
        except Exception as e:
            print("Had exception during processing: {}".format(e))

        processed = processed + length
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', action='store', help='The location of the MGST folders for TES')
    parser.add_argument('--out_dir', action='store', help='The location where outliers are stored')

    parser.add_argument('--from', action='store', help='Python style slice of the folders to process. \
                            Folders are ordered (e.g. [mgst1100, mgst1101 ...])', default=327, type=int)
    parser.add_argument('--to', action='store', help='Python style slice of the folders to process. \
                        Folders are ordered (e.g. [mgst1100, mgst1101 ...])', default=0, type=int)
    parser.add_argument('--csv', action='store', help='set to True if csv files are inputs', default=False, type=bool)

    args = parser.parse_args()
    args = args.__dict__
    print(args)
    to_mongodb(args["data_dir"], args["out_dir"], slice(args["from"], args["to"]), arsg['csv'])
