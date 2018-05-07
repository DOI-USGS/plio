import os
import warnings
import numpy as np

from plio.examples import get_path
from plio.io.io_bae import read_atf, read_gpf, read_ipf
from plio.spatial.transformations import *
import plio.io.io_controlnetwork as cn

import pandas as pd

# TODO: Change script to potentially handle configuration files

# Setup the at_file and path to cubes
cub_path = '/Volumes/Blueman/'
at_file = get_path('CTX_Athabasca_Middle_step0.atf')

# Define ipf mapping to cubs
image_dict = {'P01_001540_1889_XI_08N204W' : 'P01_001540_1889_XI_08N204W.lev1.cub',
              'P01_001606_1897_XI_09N203W' : 'P01_001606_1897_XI_09N203W.lev1.cub',
              'P02_001804_1889_XI_08N204W' : 'P02_001804_1889_XI_08N204W.lev1.cub',
              'P03_002226_1895_XI_09N203W' : 'P03_002226_1895_XI_09N203W.lev1.cub',
              'P03_002371_1888_XI_08N204W' : 'P03_002371_1888_XI_08N204W.lev1.cub',
              'P19_008344_1894_XN_09N203W' : 'P19_008344_1894_XN_09N203W.lev1.cub',
              'P20_008845_1894_XN_09N203W' : 'P20_008845_1894_XN_09N203W.lev1.cub'}

##
# End Config
##

# Read in and setup the atf dict of information
atf_dict = read_atf(at_file)

# Get the gpf and ipf files using atf dict
gpf_file = os.path.join(atf_dict['PATH'], atf_dict['GP_FILE']);
ipf_list = [os.path.join(atf_dict['PATH'], i) for i in atf_dict['IMAGE_IPF']]

# Read in the gpf file and ipf file(s) into seperate dataframes
gpf_df = read_gpf(gpf_file)
ipf_df = read_ipf(ipf_list)

# Check for differences between point ids using each dataframes
# point ids as a reference
gpf_pt_idx = pd.Index(pd.unique(gpf_df['point_id']))
ipf_pt_idx = pd.Index(pd.unique(ipf_df['pt_id']))

point_diff = ipf_pt_idx.difference(gpf_pt_idx)

if len(point_diff) != 0:
    warnings.warn("The following points found in ipf files missing from gpf file: \n\n{}. \
                  \n\nContinuing, but these points will be missing from the control network".format(list(point_diff)))

# Merge the two dataframes on their point id columns
socet_df = ipf_df.merge(gpf_df, left_on='pt_id', right_on='point_id')

# Apply the transformations
apply_transformations(atf_dict, socet_df)

# Define column remap for socet dataframe
column_remap = {'l.': 'y', 's.': 'x',
                'res_l': 'LineResidual', 'res_s': 'SampleResidual', 'known': 'Type',
                'lat_Y_North': 'AprioriY', 'long_X_East': 'AprioriX', 'ht': 'AprioriZ',
                'sig0': 'AprioriLatitudeSigma', 'sig1': 'AprioriLongitudeSigma', 'sig2': 'AprioriRadiusSigma'}

# Rename the columns using the column remap above
socet_df.rename(columns = column_remap, inplace=True)

images = pd.unique(socet_df['ipf_file'])

serial_dict = serial_numbers(image_dict, cub_path)

# creates the control network
cn.to_isis('/Volumes/Blueman/test.net', socet_df, serial_dict)
