# -*- coding: utf-8 -*-
"""
Modified by Joan Mas Colomer,
from the code written by the pyNastran Developers.

Copyright (c) 2017 pyNastran Developers. All rights reserved.

Copyright (c) 2018, ONERA
All rights reserved.
Copyright (c) 2018, ISAE
All rights reserved.
Copyright (c) 2018, Joan Mas Colomer
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

a. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. b. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. c. Neither the name of the pyNastran developers nor the names of any contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Defines functions for single precision 8 character field writing.
"""
from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
from six import string_types, integer_types
from six.moves import range
import sys
from numpy import float32, isnan


def set_string8_blank_if_default(value, default):
    """helper method for writing BDFs"""
    val = set_blank_if_default(value, default)
    if val is None:
        return '        '
    return '%8s' % val


def is_same(value1, value2):
    """
    Checks to see if 2 values are the same

    .. note:: this method is used by almost every card when printing
    """
    if isinstance(value1, string_types) or value1 is None:
        return True if value1 == value2 else False
    if value1 == value2:
        return True
    return False


def set_blank_if_default(value, default):
    """
    Used when setting the output data of a card to clear default values

    Parameters
    ----------
    value : int/float/str
        the field value the may be set to None (blank)
        if value=default, the default value for the field
    default : int/float/str
        the default value

    .. note:: this method is used by almost every card when printing
    """
    if isinstance(value, (float, float32)) and isnan(value):
        return None
    return None if is_same(value, default) else value


def set_default_if_blank(value, default):
    """
    Used when initializing a card and the default value isn't set
    Used on PBARL
    """
    return default if value is None or value == '' else value


def print_scientific_8(value):
    """
    Prints a value in 8-character scientific notation.
    This is a sub-method and shouldnt typically be called

    .. seealso:: :func: `print_float_8` for a better method
    """
    if value == 0.0:
        return '%8s' % '0.'

    python_value = '%8.11e' % value
    svalue, sexponent = python_value.strip().split('e')
    exponent = int(sexponent)  # removes 0s

    sign = '-' if abs(value) < 1. else '+'

    # the exponent will be added later...
    exp2 = str(exponent).strip('-+')
    value2 = float(svalue)

    leftover = 4 - len(exp2)

    if value < 0:
        fmt = "%%1.%sf" % (leftover - 1)
    else:
        fmt = "%%1.%sf" % leftover

    svalue3 = fmt % value2
    svalue4 = svalue3.strip('0')
    field = "%8s" % (svalue4 + 'E' + sign + exp2)
    return field


def print_float_8(value):
    """
    Prints a float in nastran 8-character width syntax using the
    highest precision possbile.
    """
    if isnan(value):
        return '        '
    elif value == 0.0:
        return '%8s' % '0.'
    elif value > 0.:  # positive, not perfect...
        if value < 5e-8:
            field = print_scientific_8(value)
            return field
        elif value < 0.0001:
            field = print_scientific_8(value)
            field2 = "%8.7f" % value  # small value
            field2 = field2.strip('0 ')

            field1 = field

            if field2 == '.':
                return print_scientific_8(value)
            if len(field2) <= 8 and float(field1) == float(field2):
                field = field2
                field = field.strip(' 0')
        elif value < 0.1:
            field = "%8.7f" % value
        elif value < 1.:
            field = "%8.7f" % value  # same as before...
        elif value < 10.:
            field = "%8.6f" % value
        elif value < 100.:
            field = "%8.5f" % value
        elif value < 1000.:
            field = "%8.4f" % value
        elif value < 10000.:
            field = "%8.3f" % value
        elif value < 100000.:
            field = "%8.2f" % value
        elif value < 1000000.:
            field = "%8.1f" % value
        else:  # big value
            field = "%8.1f" % value
            if field.index('.') < 8:
                field = '%8.1f' % round(value)
                field = field[0:8]
                #assert '.' != field[0], field
            else:
                field = print_scientific_8(value)
            return field
    else:
        if value > -5e-7:
            field = print_scientific_8(value)
            return field
        elif value > -0.001:  # -0.001
            field = print_scientific_8(value)
            field2 = "%8.6f" % value  # small value
            field2 = field2.strip('0 ')

            # get rid of the first minus sign, add it on afterwards
            field1 = field

            if len(field2) <= 8 and float(field1) == float(field2):
                field = field2.rstrip(' 0')
                field = field.replace('-0.', '-.')

        elif value > -0.1:
            # -0.01 >x>-0.1...should be 5 (maybe scientific...)
            field = "%8.6f" % value
            field = field.replace('-0.', '-.')
        elif value > -1.:
            # -0.1  >x>-1.....should be 6, but the baseline 0 is kept...
            field = "%8.6f" % value
            field = field.replace('-0.', '-.')
        elif value > -10.:
            field = "%8.5f" % value   # -1    >x>-10
        elif value > -100.:
            field = "%8.4f" % value   # -10   >x>-100
        elif value > -1000.:
            field = "%8.3f" % value   # -100  >x>-1000
        elif value > -10000.:
            field = "%8.2f" % value   # -1000 >x>-10000
        elif value > -100000.:
            field = "%8.1f" % value   # -10000>x>-100000
        else:
            field = "%8.1f" % value
            try:
                ifield = field.index('.')
            except ValueError:
                raise ValueError('error printing float; cant find decimal; field=%r value=%s' % (field, value))
            if ifield < 8:
                field = '%7s.' % int(round(value, 0))
                #assert '.' != field[0], field
            else:
                field = print_scientific_8(value)
            return field
    field = field.strip(' 0')
    field = '%8s' % field

    #assert len(field) == 8, ('value=|%s| field=|%s| is not 8 characters '
    #                         'long, its %s' % (value, field, len(field)))
    return field


def print_float_or_int_8(value):
    """
    Prints a 8-character width field

    Parameters
    ----------
    value : int/float
        the value to print

    Returns
    -------
    field : str
        an 8-character string
    """
    if isinstance(value, (float, float32)):
        field = print_float_8(value)
    elif isinstance(value, integer_types):
        field = "%8i" % value
    else:
        msg = 'Invalid Type:  value=%r type=%s' % (value, type(value))
        raise TypeError(msg)


def print_field_8(value):
    """
    Prints a 8-character width field

    Parameters
    ----------
    value : int/float/str
        the value to print

    Returns
    -------
    field : str
        an 8-character string
    """
    if isinstance(value, integer_types):
        field = "%8i" % value
    elif isinstance(value, (float, float32)):
        field = print_float_8(value)
    elif value is None:
        field = "        "
    else:
        field = "%8s" % value
    if len(field) != 8:
        msg = 'field=%r is not 8 characters long...raw_value=%r' % (field, value)
        raise RuntimeError(msg)
    return field


def print_card_8(fields):
    """
    Prints a nastran-style card with 8-character width fields.

    Parameters
    ----------
    fields : List[int/float/str/None]
        all the fields in the BDF card (no trailing Nones)

    Returns
    -------
    card : str
        string representation of the card in small field format

    .. note:: An internal field value of None or '' will be treated as
              a blank field
    .. note:: A small field format follows the  8-8-8-8-8-8-8-8 = 80
              format where the first 8 is the card name or
              blank (continuation).  The last 8-character field indicates
              an optional continuation, but because it's a left-justified
              unneccessary field, print_card doesnt use it.

    .. code-block:: python

      >>> fields = ['DUMMY', 1, 2, 3, None, 4, 5, 6, 7, 8.]
      >>> print_card_8(fields)
      DUMMY          1       2       3               4       5       6       7
      DUMMY          1       2       3               4       5       6       7
                    8.
    """
    try:
        out = '%-8s' % fields[0]
    except:
        print("ERROR!  fields=%s" % fields)
        sys.stdout.flush()
        raise

    for i in range(1, len(fields)):
        field = fields[i]
        try:
            out += print_field_8(field)
        except:
            print("bad fields = %s" % fields)
            raise
        if i % 8 == 0:  # allow 1+8 fields per line
            out = out.rstrip(' ')
            if out[-1] == '\n':  # empty line
                out += '+'
            out += '\n        '
    out = out.rstrip(' \n+') + '\n'  # removes blank lines at the end of cards
    return out


def print_int_card(fields):
    """
    Prints a nastran-style card with 8-character width fields.
    All fields (other than the first field) must be integers.
    This is used to speed up SET cards.

    Parameters
    ----------
    fields : List[int/float/str/None]
      The list of fields to write to a nastran card.

    .. warning::
      Blanks are not allowed!
      Floats and strings are not allowed.

    .. code-block:: python

      fields = ['SET', 1, 2, 3, 4, 5, 6, ..., n]
    """
    try:
        out = '%-8s' % fields[0]
    except:
        print("ERROR!  fields=%s" % fields)
        sys.stdout.flush()
        raise

    for i in range(1, len(fields)):
        field = fields[i]
        try:
            out += "%8i" % field  # balks if you have None or string fields
        except:
            print("bad fields = %s" % fields)
            raise
        if i % 8 == 0:  # allow 1+8 fields per line
            out = out.rstrip(' ')
            out += '\n        '
    out = out.rstrip(' \n+') + '\n'  # removes blank lines at the end of cards
    return out


def print_int_card_blocks(fields_blocks):
    """
    Prints a nastran-style card with 8-character width fields.
    All fields other than the card name must be written in "block" format.
    This is used to speed up SET cards.

    Parameters
    ----------
    fields_blocks : List[int]
      The fields written in "block" notation.

    Returns
    -------
    msg : str
        the field blocks as a 8-character width Nastran card

    .. note:: Blanks are allowed in the False block.

    .. code-block:: python

      fields_blocks = [
          'SET1',
          [['a', 1.0, 3], False], # these are not all integers
          [[1, 2, 3], True],      # these are all integers
      ]
      msg = print_int_card_blocks(fields_blocks)
      print(msg)
      >>> 'SET1           a      1.       3       1       2       3\n'

    """
    card_name = fields_blocks[0]
    try:
        out = '%-8s' % card_name
    except:
        print("ERROR!  fields_blocks=%s" % fields_blocks)
        sys.stdout.flush()
        raise

    i = 0
    for block in fields_blocks[1:]:
        (fields, is_all_ints) = block
        if is_all_ints is True:
            for field in fields:
                out += "%8i" % field
                i += 1
                if i == 8:  # allow 1+8 fields per line
                    out += '\n        '
                    i = 0
        elif is_all_ints is False:
            for field in fields:
                out += print_field_8(field)
                i += 1
                if i == 8:  # allow 1+8 fields per line
                    out += '\n        '
                    i = 0
        else:
            raise SyntaxError('is_all_ints must be a boolean.  is_all_ints=%r' % is_all_ints)
    out = out.rstrip(' \n') + '\n'  # removes blank lines at the end of cards
    return out
