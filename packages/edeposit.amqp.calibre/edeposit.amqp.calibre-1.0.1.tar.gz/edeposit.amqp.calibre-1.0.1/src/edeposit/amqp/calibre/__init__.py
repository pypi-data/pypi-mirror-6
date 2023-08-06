#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
AMQP communication wrapper for calibre's ``ebook-convert`` program.
"""
from collections import namedtuple


import calibre


#= Variables ==================================================================
INPUT_FORMATS = [
    "cbz",
    "cbr",
    "cbc",
    "chm",
    "djvu",
    "docx",
    "epub",
    "fb2",
    "html",
    "htmlz",
    "lit",
    "lrf",
    "mobi",
    "odt",
    "pdf",
    "prc",
    "pdb",
    "pml",
    "rb",
    "rtf",
    "snb",
    "tcr",
    "txt",
    "txtz"
]
"List of `available input <http://bit.ly/1c1bHZP>`_ formats."

OUTPUT_FORMATS = [  #:
    "azw3",
    "epub",
    "fb2",
    "oeb",
    "lit",
    "lrf",
    "mobi",
    "htmlz",
    "pdb",
    "pml",
    "rb",
    "pdf",
    "rtf",
    "snb",
    "tcr",
    "txt",
    "txtz"
]
"List of `available output <http://bit.ly/1c1bHZP>`_ formats."


#= Functions & objects ========================================================
class ConversionRequest(namedtuple("ConversionRequest", ["input_format",
                                                         "output_format",
                                                         "b64_data"])):
    """
    This structure specifies details of AMQP message, which is passed to
    :func:`reactToAMQPMessage` as request for conversion.

    Args:
        input_format (str):  see :attr:`INPUT_FORMATS` for list of valid input
                             formats
        output_format (str): see :attr:`OUTPUT_FORMATS` for list of valid output
                             formats
        b64_data (base64 str): :py:mod:`base64` encoded file

    Raises:
        ValueError: if invalid input/output format is provided.
    """
    def __init__(self, input_format, output_format, b64_data):
        if input_format not in INPUT_FORMATS:
            raise ValueError("Unsupported input format!")

        if output_format not in OUTPUT_FORMATS:
            raise ValueError("Unsupported output format!")

        if input_format == output_format:
            raise ValueError("Input and output formats are the same.")


class ConversionResponse(namedtuple("ConversionResponse", ["format",
                                                           "b64_data",
                                                           "protocol"])):
    """
    Structure is returned as response from :func:`reactToAMQPMessage`, when
    the file is converted.

    Args:
        type (str): see OUTPUT_FORMATS for details
        b64_data (base64 str): :py:mod:`base64` encoded converted data
        protocol (str): protocol of the conversion
    """
    pass


def _instanceof(instance, class_):
    """Check type by matching ``.__name__``."""
    type(instance).__name__ == class_.__name__


def reactToAMQPMessage(message, UUID):
    """
    React to given (AMQP) message. `message` is usually expected to be
    :py:func:`collections.namedtuple` structure filled with all necessary data.

    Args:
        message (\*Request class): only :class:`ConversionRequest` class is
                                  supported right now
        UUID (str): unique ID of received message

    Returns:
        ConversionResponse: response filled with data about conversion and\
                            converted file.

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    if _instanceof(message, ConversionRequest):
        return calibre.convert(
            message.input_format,
            message.output_format,
            message.b64_data
        )

    raise ValueError(
        "Unknown type of request: '" + str(type(message)) + "'!"
    )
