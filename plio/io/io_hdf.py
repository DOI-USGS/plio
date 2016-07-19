import h5py as h5
import numpy as np
import pandas as pd


DEFAULT_COMPRESSION = 'gzip'
DEFAULT_COMPRESSION_VALUE = 8  # 0 - 9


class HDFDataset(h5.File):
    """
    Read / Write an HDF5 dataset using h5py.  If HDF5 is compiled with
    parallel support, this class will support parallel I/O of all supported
    types as well as Pandas dataframes.
    """

    def __init__(self, filename, mode='a'):
        super(HDFDataset, self).__init__(filename, mode)

    def __del__(self):
        self.close()

    @staticmethod
    def df_to_sarray(df):
        """
        Convert a pandas DataFrame object to a numpy structured array.
        This is functionally equivalent to but more efficient than
        np.array(df.to_array())

        From: http://stackoverflow.com/questions/30773073/save-pandas-dataframe-using-h5py-for-interoperabilty-with-other-hdf5-readers

        Parameters
        ----------
        df : dataframe
             the data frame to convert

        Returns
        -------
        z : ndarray
            a numpy structured array representation of df
        """
        v = df.values
        cols = df.columns
        types = [(cols[i], df[k].dtype.type) for (i, k) in enumerate(cols)]
        dtype = np.dtype(types)
        z = np.zeros(v.shape[0], dtype)
        for (i, k) in enumerate(z.dtype.names):
            z[k] = v[:, i]
        return z

    @staticmethod
    def sarray_to_df(sarray, index_column='index'):
        """
        Convert from a structured array back to a Pandas Dataframe

        Parameters
        ----------
        sarray : array
                 numpy structured array

        index_column : str
                       The name of the index column.  Default: 'index'

        Returns
        -------
         : dataframe
           A pandas dataframe
        """

        def remove_field_name(a, name):
            names = list(a.dtype.names)
            if name in names:
                names.remove(name)
            b = a[names]
            return b
        if index_column is not None:
            index = sarray[index_column]
            clean_array = remove_field_name(sarray, 'index')
        else:
            clean_array = sarray
            index = None
        columns = clean_array.dtype.names

        return pd.DataFrame(data=sarray, index=index, columns=columns)
