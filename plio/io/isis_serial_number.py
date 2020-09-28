import warnings

import pvl
from pvl.collections import PVLModule

import plio
from plio.data import get_data
from plio.io.io_db import Translations, StringToMission, setup_db_session
from plio.utils.utils import find_in_dict, find_nested_in_dict
from datetime import datetime


def get_isis_translation(label):
    """
    Compute the ISIS serial number for a given image using
    the input cube or the label extracted from the cube.

    Parameters
    ----------
    label : dict or str
            A PVL dict object or file name to extract
            the PVL object from

    Returns
    -------
    translation : dict
                  A PVLModule object containing the extracted
                  translation file
    """
    # Instantiate a DB session if not already instantiated
    if not hasattr(plio, 'data_session'):
        plio.data_session = setup_db_session(get_data('data.db'))

    # Grab the label is not already read
    if not isinstance(label, PVLModule):
        label = pvl.load(label)

    # Grab the spacecraft name and run it through the ISIS lookup
    spacecraft_name = find_in_dict(label, 'SpacecraftName')
    for row in plio.data_session.query(StringToMission).filter(StringToMission.key==spacecraft_name):
        spacecraft_name = row.value.lower()
    # Try and pull an instrument identifier
    try:
        instrumentid = find_in_dict(label, 'InstrumentId').capitalize()
    except:
        instrumentid = None

    translation = None
    # Grab the translation PVL object using the lookup
    for row in plio.data_session.query(Translations).filter(Translations.mission==spacecraft_name,
                                                            Translations.instrument==instrumentid):
        # Convert the JSON back to a PVL object
        translation = PVLModule(row.translation)
    return translation


def generate_serial_number(label):
    """
    Generate an ISIS compatible serial number using the ISIS
    team's translation files

    Parameters
    ----------
    label : dict or str
            A PVLModule object (dict) or string PATH
            to a file containing a PVL header

    Returns
    -------
     : str
       The ISIS compatible serial number
    """
    if not isinstance(label, PVLModule):
        label = pvl.load(label, decoder=SerialNumberDecoder())
    # Get the translation information
    translation = get_isis_translation(label)

    if not translation:
        warnings.warn('Unable to load an appropriate image translation.')
        return

    serial_number = []

    # Sort the keys to ensure proper iteration order
    keys = sorted(translation.keys())

    for k in keys:
        try:
            group = translation[k]
            search_key = group['InputKey']
            search_position = group['InputPosition']
            search_translation = {group['Translation'][1]:group['Translation'][0]}
            sub_group = find_nested_in_dict(label, search_position)
            serial_entry = sub_group[search_key]

            if serial_entry in search_translation.keys():
                serial_entry = search_translation[serial_entry]
            elif '*' in search_translation.keys() and search_translation['*'] != '*':
                serial_entry = search_translation['*']
            try:
                serial_entry = serial_entry.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            except:
                pass
            serial_number.append(serial_entry)
        except:
            pass


    print(serial_number)
    return '/'.join(serial_number)


class SerialNumberDecoder(pvl.decoder.PVLDecoder):
    """
    A PVL Decoder class to handle cube label parsing for the purpose of creating a valid ISIS
    serial number. Inherits from the PVLDecoder in planetarypy's pvl module.
    """

    def cast_unquoted_string(self, value):
        """
        Overrides the parent class's method so that any un-quoted string type value found in the
        parsed pvl will just return the original value. This is needed so that keyword values
        are not re-formatted from what is originally in the ISIS cube label.

        Note: This affects value types that are recognized as null, boolean, number, datetime,
        et at.
        """
        return value.decode('utf-8')
