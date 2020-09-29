import warnings

import pvl
from pvl.collections import PVLModule
from itertools import chain

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
            serial_number.append(serial_entry)
        except:
            pass

    return '/'.join(serial_number)


class SerialNumberDecoder(pvl.decoder.PVLDecoder):
    """
    A PVL Decoder class to handle cube label parsing for the purpose of creating a valid ISIS
    serial number. Inherits from the PVLDecoder in planetarypy's pvl module.
    """

    def decode_simple_value(self, value: str):
        """Returns a Python object based on *value*, assuming
        that *value* can be decoded as a PVL Simple Value::

         <Simple-Value> ::= (<Numeric> | <String>)

         Modified from https://pvl.readthedocs.io/en/stable/_modules/pvl/decoder.html#PVLDecoder.decode_simple_value
         Modification entails stripping datetime from list of functions.
        """
        for d in (
            self.decode_quoted_string,
            self.decode_non_decimal,
            self.decode_decimal,
        ):
            try:
                return d(value)
            except ValueError:
                pass

        if value.casefold() == self.grammar.none_keyword.casefold():
            return None

        if value.casefold() == self.grammar.true_keyword.casefold():
            return True

        if value.casefold() == self.grammar.false_keyword.casefold():
            return False

        return self.decode_unquoted_string(value)

    def decode_unquoted_string(self, value: str) -> str:
        """Returns a Python ``str`` if *value* can be decoded
        as an unquoted string, based on this decoder's grammar.
        Raises a ValueError otherwise.

        Modified from: https://pvl.readthedocs.io/en/stable/_modules/pvl/decoder.html#PVLDecoder.decode_unquoted_string
        Modification entails removal of decode_datetime call
        """
        for coll in (
            ("a comment", chain.from_iterable(self.grammar.comments)),
            ("some whitespace", self.grammar.whitespace),
            ("a special character", self.grammar.reserved_characters),
        ):
            for item in coll[1]:
                if item in value:
                    raise ValueError(
                        "Expected a Simple Value, but encountered "
                        f'{coll[0]} in "{self}": "{item}".'
                    )

        agg_keywords = self.grammar.aggregation_keywords.items()
        for kw in chain.from_iterable(agg_keywords):
            if kw.casefold() == value.casefold():
                raise ValueError(
                    "Expected a Simple Value, but encountered "
                    f'an aggregation keyword: "{value}".'
                )

        for es in self.grammar.end_statements:
            if es.casefold() == value.casefold():
                raise ValueError(
                    "Expected a Simple Value, but encountered "
                    f'an End-Statement: "{value}".'
                )

        return str(value)
