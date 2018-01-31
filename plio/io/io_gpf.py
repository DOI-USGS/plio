import math
import numpy as np
import pandas as pd


GPF_DATA_DTYPE = np.dtype([('point_id', np.int), ('stat', np.int), ('known', np.int),
                  ('lat_Y_North', np.float), ('long_X_East', np.float), ('ht', np.float),
                  ('sigma0', np.float), ('sigma1', np.float), ('sigma2', np.float),
                  ('res0', np.float), ('res1', np.float), ('res2', np.float)])


def read_gpf(input_data):
    """
    Read a socet gpf file into a pandas data frame

    Parameters
    ----------
    input_file : str
                 path to the input data file

    Returns
    -------
    df : pd.DataFrame
         containing the gfp data with appropriate column names and indices
    """

    # Mixed types requires read as unicode - let pandas soft convert
    d = np.genfromtxt(input_data, skip_header=3, dtype='unicode')
    d = d.reshape(-1, 12)

    #TODO: cols should be used to dynamically generate the column names

    df = pd.DataFrame(d, columns=['point_id', 'stat', 'known',
                              'lat_y_North', 'long_X_East','ht',
                              'sigma0', 'sigma1', 'sigma2',
                              'res0', 'res1', 'res2'])
    # Soft conversion of numeric types to numerics
    df = df.apply(pd.to_numeric, errors='ignore')
    return df




# def GPF_SAV(input_data, ave=True):
    # # read the IDL .SAV file

    # data = io.readsav(input_data, python_dict=True)

    # # put the spectra into data frames and combine them
    # df_UV = pd.DataFrame(data['uv'], index=data['defuv'])
    # df_VIS = pd.DataFrame(data['vis'], index=data['defvis'])
    # df_VNIR = pd.DataFrame(data['vnir'], index=data['defvnir'])
    # df_spect = pd.concat([df_UV, df_VIS, df_VNIR])
    # df_spect.columns = ['shot' + str(i + 1) for i in
                        # df_spect.columns]  # add 1 to the columns so they correspond to shot number

    # df_aUV = pd.DataFrame(data['auv'], index=data['defuv'], columns=['average'])
    # df_aVIS = pd.DataFrame(data['avis'], index=data['defvis'], columns=['average'])
    # df_aVNIR = pd.DataFrame(data['avnir'], index=data['defvnir'], columns=['average'])
    # df_ave = pd.concat([df_aUV, df_aVIS, df_aVNIR])

    # df_mUV = pd.DataFrame(data['muv'], index=data['defuv'], columns=['median'])
    # df_mVIS = pd.DataFrame(data['mvis'], index=data['defvis'], columns=['median'])
    # df_mVNIR = pd.DataFrame(data['mvnir'], index=data['defvnir'], columns=['median'])
    # df_med = pd.concat([df_mUV, df_mVIS, df_mVNIR])

    # df = pd.concat([df_spect, df_ave, df_med], axis=1)
    # # create multiindex to access wavelength values
    # # also, round the wavlength values to a more reasonable level of precision
    # df.index = [['wvl'] * len(df.index), df.index.values.round(4)]
    # # transpose so that spectra are rows rather than columns
    # df = df.T

    # # extract metadata from the file name and add it to the data frame
    # # use the multiindex label "meta" for all metadata

    # fname = os.path.basename(input_data)

    # # for some reason, some ChemCam files have the 'darkname' key, others call it 'darkspect'
    # # this try-except pair converts to 'darkname' when needed
    # try:
        # data['darkname']
    # except:
        # data['darkname'] = data['darkspec']

    # metadata = [fname,
                # fname[4:13],
                # fname[25:34].upper(),
                # fname[34:36],
                # data['continuumvismin'],
                # data['continuumvnirmin'],
                # data['continuumuvmin'],
                # data['continuumvnirend'],
                # data['distt'],
                # data['darkname'],
                # data['nshots'],
                # data['dnoiseiter'],
                # data['dnoisesig'],
                # data['matchedfilter']]
    # metadata = np.tile(metadata, (len(df.index), 1))
    # metadata_cols = list(zip(['meta'] * len(df.index), ['file',
                                                        # 'sclock',
                                                        # 'seqid',
                                                        # 'Pversion',
                                                        # 'continuumvismin',
                                                        # 'continuumvnirmin',
                                                        # 'continuumuvmin',
                                                        # 'continuumvnirend',
                                                        # 'distt',
                                                        # 'dark',
                                                        # 'nshots',
                                                        # 'dnoiseiter',
                                                        # 'dnoisesig',
                                                        # 'matchedfilter']))
    # metadata = pd.DataFrame(metadata, columns=pd.MultiIndex.from_tuples(metadata_cols), index=df.index)

    # df = pd.concat([metadata, df], axis=1)
    # if ave == True:
        # df = df.loc['average']
        # df = df.to_frame().T
    # else:
        # pass

    # return df


# def ccam_batch(directory, searchstring='*.csv', to_csv=None, lookupfile=None, ave=True, progressbar=None):
    # # Determine if the file is a .csv or .SAV
    # if '.sav' in searchstring.lower():
        # is_sav = True
    # else:
        # is_sav = False
    # filelist = file_search(directory, searchstring)
    # basenames = np.zeros_like(filelist)
    # sclocks = np.zeros_like(filelist)
    # P_version = np.zeros_like(filelist, dtype='int')

    # # Extract the sclock and version for each file and ensure that only one
    # # file per sclock is being read, and that it is the one with the highest version number
    # for i, name in enumerate(filelist):
        # basenames[i] = os.path.basename(name)
        # sclocks[i] = basenames[i][4:13]  # extract the sclock
        # P_version[i] = basenames[i][-5:-4]  # extract the version

    # sclocks_unique = np.unique(sclocks)  # find unique sclocks
    # filelist_new = np.array([], dtype='str')
    # for i in sclocks_unique:
        # match = (sclocks == i)  # find all instances with matching sclocks
        # maxP = P_version[match] == max(P_version[match])  # find the highest version among these files
        # filelist_new = np.append(filelist_new, filelist[match][maxP])  # keep only the file with thei highest version

    # filelist = filelist_new
    # # Should add a progress bar for importing large numbers of files
    # dt = []

    # for i, file in enumerate(filelist):
        # print(file)
        # if is_sav:
            # tmp = CCAM_SAV(file, ave=ave)
        # else:
            # tmp = CCAM_CSV(file, ave=ave)
        # if i == 0:
            # combined = tmp
        # else:
            # # This ensures that rounding errors are not causing mismatches in columns
            # cols1 = list(combined['wvl'].columns)
            # cols2 = list(tmp['wvl'].columns)
            # if set(cols1) == set(cols2):
                # combined = pd.concat([combined, tmp])
            # else:
                # print("Wavelengths don't match!")

    # combined.loc[:, ('meta', 'sclock')] = pd.to_numeric(combined.loc[:, ('meta', 'sclock')])

    # if lookupfile is not None:

        # combined = lookup(combined, lookupfile=lookupfile.replace('[','').replace(']','').replace("'",'').replace(' ','').split(','))
    # if to_csv is not None:
        # combined.to_csv(to_csv)
    # return combined



# main(int argc, char *argv[])
# {

  # char     gpfFile[FILELEN];
  # char     csvFile[FILELEN];
  # char     pointIDsFile[FILELEN];

  # FILE     *gpfFp;     // file pointer to input csv file
  # FILE     *csvFp;     // file pointer to output csv file
  # FILE     *ptsFp;     // file pointer to output point ids list file

  # char     gpfLine[LINELENGTH];

  # // check number of command line args and issue help if needed
  # //-----------------------------------------------------------
  # if (argc != 2) {
     # printf ("\nrun %s as follows:\n",argv[0]);
     # printf ("   %s SSgpfFile\n",
             # argv[0]);
     # printf ("\nwhere:\n");
     # printf ("  SSgpfFile = Socet Set *.gpf file, from a geographic project\n\n");
     # printf ("  This program will convert a Socet Set ground point file into a CSV\n");
     # printf ("  of lat,lon,height.  The output file will have the same core name\n");
     # printf ("  of the input *.gpf file, but with a .csv extension\n\n");
     # printf ("  Also output is the list of point IDs that were converted.  This file\n");
     # printf ("  will be used to port the points back to Socet Set later on.  The output\n");
     # printf ("  file will have the same core name as the input file, but with a .pointids\n");
     # printf ("  .tiePointIds.txt extension.\n");
     # exit(1);
  # }

  # //------------------------------------------------
  # // get input arguments entered at the command line
  # //------------------------------------------------

  # strcpy (gpfFile,argv[1]);

  # //-----------------------------
  # // generate ouput file names
  # //-----------------------------

  # char corename[FILELEN];
  # strcpy (corename,gpfFile);
  # int len = strlen(corename);
  # corename[len-4] = '\0';

  # strcpy (csvFile,corename);
  # strcat (csvFile,".csv");

  # strcpy (pointIDsFile,corename);
  # strcat (pointIDsFile,".tiePointIds.txt");

  # /////////////////////////////////////////////////////////////////////////////
  # // open files
  # /////////////////////////////////////////////////////////////////////////////

  # gpfFp = fopen (gpfFile,"r");
  # if (gpfFp == NULL) {
    # printf ("unable to open input gpf file: %s\n",gpfFile);
    # exit (1);
  # }

  # csvFp = fopen (csvFile,"w");
  # if (csvFp == NULL) {
    # printf ("unable to open output csv file: %s\n",csvFile);
    # fclose(gpfFp);
    # exit (1);
  # }

  # ptsFp = fopen (pointIDsFile,"w");
  # if (csvFp == NULL) {
    # printf ("unable to open output list file of tie point ids: %s\n",pointIDsFile);
    # fclose(gpfFp);
    # fclose(csvFp);
    # exit (1);
  # }

  # //------------------------------------------------
  # //------------------------------------------------

  # // skip the header
  # fgets(gpfLine,LINELENGTH,gpfFp);

  # // read in number of points in *.gpf file
  # char value[50];
  # fgets(gpfLine,LINELENGTH,gpfFp);
  # sscanf (gpfLine,"%s",value);
  # int numpts = atoi(value);

  # // skip next header
  # fgets(gpfLine,LINELENGTH,gpfFp);

  # // Parse gpf, output csv
  # char pointID[50], valStat[2], valKnown[2];
  # char valLon[50], valLat[50], Height[50];
  # double rad2dd = 57.295779513082320876798154814105;

  # for (int i=0; i<numpts; i++) {
    # fgets(gpfLine,LINELENGTH,gpfFp);
    # sscanf (gpfLine,"%s %s %s",pointID,valStat,valKnown);
    # int stat = atoi(valStat);
    # int known = atoi(valKnown);

    # // get coordinate
    # fgets(gpfLine,LINELENGTH,gpfFp);

    # //only output tie points that are on
    # if (stat == 1 && known == 0) {
      # sscanf (gpfLine,"%s %s %s",valLat,valLon,Height);
      # double radLat = atof(valLat);
      # double radLon = atof(valLon);
      # fprintf(csvFp,"%.14lf,%.14lf,%s\n",rad2dd*radLat,rad2dd*radLon,Height);
      # fprintf(ptsFp,"%s\n",pointID);
    # }

    # // skip next three lines in input *.gpf file
    # for (int j=0; j<3; j++)
      # fgets(gpfLine,LINELENGTH,gpfFp);
  # }

  # fclose(gpfFp);
  # fclose(csvFp);

# } // end of program
