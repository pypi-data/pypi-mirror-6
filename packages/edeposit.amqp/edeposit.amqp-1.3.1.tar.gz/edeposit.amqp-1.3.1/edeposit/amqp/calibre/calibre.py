#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
Lowlevel conversion API for calibre's ``ebook-convert``.
"""
import os
from base64 import b64encode, b64decode
from tempfile import NamedTemporaryFile as NTFile


import sh


from __init__ import INPUT_FORMATS, OUTPUT_FORMATS, ConversionResponse


#= Functions & objects ========================================================
def check_ebook_convert():
    """
    Check, if the ``ebook-convert`` program is installed.

    Raises:
        UserWarning: if not.
    """
    try:
        output = sh.ebook_convert(_ok_code=[1])
    except sh.CommandNotFound:
        raise UserWarning(
            "'ebook-convert' not found. Do you have callibre installed?"
        )

    # check whether the output is really from ebook-convert
    if "Usage" not in output or "Convert an ebook" not in output:
        raise UserWarning(
            "'ebook-convert' reacts strangely. Post this to developers:\n\n" +
            b64encode(str(output))
        )


def convert(input_format, output_format, b64_data):
    """
    Convert `b64_data` fron `input_format` to `output_format`.

    Args:
        input_format (str):  specification of input format (pdf/epub/whatever),
                             see :attr:`__init__.INPUT_FORMATS` for list
        output_format (str): specification of output format (pdf/epub/whatever),
                             see :attr:`__init__.OUTPUT_FORMATS` for list
        b64_data (str):      base64 encoded data

    Returns:
        ConversionResponse: namedtuple structure with information about output\
                            ``format``, data (``b64_data``) and ``protocol``\
                            from conversion. Structure is defined in \
                            :class:`.ConversionResponse`.

    Raises:
        AssertionError: when bad arguments are handed over
        UserWarning: when conversion failed
    """
    # checks
    assert input_format in INPUT_FORMATS, "Unsupported input format!"
    assert output_format in OUTPUT_FORMATS, "Unsupported output format!"
    assert input_format != output_format, "Input and output formats are same!"

    with NTFile(mode="wb", suffix="." + input_format, dir="/tmp") as ifile:
        ofilename = ifile.name + "." + output_format

        # save received data to the temporary file
        ifile.write(
            b64decode(b64_data)
        )

        # convert file
        output = sh.ebook_convert(ifile.name, ofilename)

        if output_format.upper() + " output written to" not in output:
            raise UserWarning("Conversion failed:\n" + output)

        # read the data from the converted file
        output_data = None
        with open(ofilename, "rb") as ofile:
            output_data = ofile.read()

        # remove temporary
        os.remove(ofilename),

        return ConversionResponse(
            format=output_format,
            b64_data=b64encode(output_data),
            protocol=str(output)
        )
