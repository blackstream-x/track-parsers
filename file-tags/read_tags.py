#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Read audio tags from local files.
Print track number, artist, song title and duration for each file,
suitable for pasting into Musicbrainz’ track parser.

Copyright (C) 2015 Rainer Schwarzbach
                   <blackstream-x@users.noreply.github.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import glob
import logging
import os
import re
import six
import sys
import taglib


__version__ = '0.5.1'


# Disable some pylint messages
# pylint: disable=logging-format-interpolation, superfluous-parens


#
# Constants
#

ALL_FILES = '*.*'
ANY_NUMBER = '*'
ELLIPSIS = u'…'
EMPTY = ''
FILE_ARGUMENT_HELP = 'Files or directories to read audio tags from'
FILE_ARGUMENT_NAME = 'File or Directory'
FIRST_INDEX = 0
IN_SQUARE_BRACKETS = r'[\1]'
LATIN1 = 'latin-1'
LOG_MESSAGE_FORMAT = '%(levelname)-8s | %(message)s'
MISSING_TAG_PLACEHOLDER = u'({0})'.format(ELLIPSIS)
MSG_HIT_ENTER = '\nPlease hit enter to close the window: '
MSG_TAGS_MISSING = 'File {0!r}: Tags missing {1}'
MSG_UNSUPPORTED_TYPE = 'File {0!r}: File type probably not supported'
NAUTILUS_SCRIPT_SELECTED_FILE_PATHS = \
    'NAUTILUS_SCRIPT_SELECTED_FILE_PATHS'
PROGRAM_DESCRIPTION = ('Read audio tags from local files and print them'
                       ' as a tracklist suitable to be copied into the'
                       ' Musicbrainz track parser')
RC_OK = 0
SECONDS_PER_MINUTE = 60
SEPARATOR = u' / '
UTF8 = 'utf-8'

#
# Precompiled regular expressions
PRX_GLOB_MAGIC = re.compile('([*?[])')
PRX_TRACKS_TOTAL = re.compile(r'/.*')

#
# Tag names as provided by the taglib module
TAG_TRACK_NUMBER = 'TRACKNUMBER'
TAG_ARTIST = 'ARTIST'
TAG_TITLE = 'TITLE'
TAG_LENGTH = 'length'
REQUIRED_TAGS = (TAG_TRACK_NUMBER, TAG_ARTIST, TAG_TITLE)

#
# Format strings
FS_0 = u'{0}'
FS_AUDIO_LENGTH = u'{0:02d}:{1:02d}'
FS_DICT_PLACEHOLDER = u'{{0[{0}]}}'
FS_TRACK = u'{0}. {1} – {2} ({3})'.format(
    FS_DICT_PLACEHOLDER.format(TAG_TRACK_NUMBER),
    FS_DICT_PLACEHOLDER.format(TAG_TITLE),
    FS_DICT_PLACEHOLDER.format(TAG_ARTIST),
    FS_DICT_PLACEHOLDER.format(TAG_LENGTH))


#
# Function definitions
#


def __avoid_latin_1(text):
    """Re-en-and -decode unicode that had been
    misinterpreted as latin-1 in its original encoding by pytaglib
    """
    return text.encode(LATIN1).decode(UTF8)


def audio_length(seconds):
    """Return audio length in mm:ss format"""
    _minutes, _seconds = divmod(int(seconds), SECONDS_PER_MINUTE)
    return FS_AUDIO_LENGTH.format(_minutes, _seconds)


def escape_for_glob(pathname):
    """Escape all special characters in the given path.
    Adapted from python 3.4 source:
    <https://hg.python.org/cpython/file/3.4/Lib/glob.py>
    """
    # Escaping is done by wrapping any of "*?[" between square brackets.
    # Metacharacters do not work in the drive part and should
    # not be escaped there.
    drive, pathname = os.path.splitdrive(pathname)
    pathname = PRX_GLOB_MAGIC.sub(IN_SQUARE_BRACKETS, pathname)
    return drive + pathname


def print_directory_tracklist(given_directory):
    """Output a tracklist from all files in the given directory.
    Files will be sorted by name before.
    """
    given_directory = to_unicode(given_directory)
    for single_file in sorted(glob.glob(os.path.join(
            escape_for_glob(given_directory), ALL_FILES))):
        print_file_tracklist(single_file)
    #


def print_file_tracklist(given_file):
    """Output the file’s audio data as a tracklist line"""
    given_file = to_unicode(given_file)
    shortened_filename = os.path.join(ELLIPSIS,
                                      os.path.basename(given_file))
    try:
        audio_data = taglib.File(given_file)
    except OSError as os_error:
        # File types the taglib cannot handle will produce an OSError.
        # Simply log the error and ignore these files.
        logging.error(os_error)
        if os.path.isfile(given_file):
            logging.info(
                MSG_UNSUPPORTED_TYPE.format(shortened_filename))
        #
    else:
        # Check for missing tags.
        # If tags are missing, log a warning message
        # and use the defined placeholder for the missing tags
        output_tags = {}
        missing_tags = []
        for single_tag in REQUIRED_TAGS:
            try:
                original_tag = audio_data.tags[single_tag]
            except KeyError:
                output_tags[single_tag] = MISSING_TAG_PLACEHOLDER
                missing_tags.append(single_tag)
            else:
                # Read only the first track number,
                # but concatenate multiple entries in the other tags
                # if necessary.
                if single_tag == TAG_TRACK_NUMBER:
                    output_tags[single_tag] = \
                        PRX_TRACKS_TOTAL.sub(EMPTY,
                                             original_tag[FIRST_INDEX])
                else:
                    fixed_tags = []
                    for tag_part in original_tag:
                        try:
                            fixed_tags.append(__avoid_latin_1(tag_part))
                        except UnicodeError:
                            fixed_tags.append(tag_part)
                        #
                    output_tags[single_tag] = \
                        SEPARATOR.join(fixed_tags)
                #
            #
        try:
            output_tags[TAG_LENGTH] = audio_length(audio_data.length)
        except AttributeError:
            output_tags[TAG_LENGTH] = ELLIPSIS
            missing_tags.append(TAG_LENGTH)
        if missing_tags:
            logging.warning(MSG_TAGS_MISSING.format(shortened_filename,
                                                    missing_tags))
        print(FS_TRACK.format(output_tags))
    #


def to_unicode(given_object, encoding=UTF8):
    """Transform any given object to unicode"""
    if isinstance(given_object, six.binary_type):
        return given_object.decode(encoding)
    elif isinstance(given_object, six.text_type):
        return given_object
    else:
        return six.text_type(given_object)
    #


#
# Main script
#


if __name__ == '__main__':
    # Process the specified files or directories
    # If no argument was given, process the current directory.
    logging.basicConfig(format=LOG_MESSAGE_FORMAT, level=logging.DEBUG)
    ARGUMENT_PARSER = \
        argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
    ARGUMENT_PARSER.add_argument(FILE_ARGUMENT_NAME,
                                 help=FILE_ARGUMENT_HELP,
                                 nargs=ANY_NUMBER)
    ARGUMENTS_LIST = getattr(ARGUMENT_PARSER.parse_args(),
                             FILE_ARGUMENT_NAME)
    try:
        # Nautilus script integration.
        # If the script gets called via Nautilus, add the selected paths
        # as if they were given as command line arguments.
        ARGUMENTS_LIST.extend(
            argument for argument in
            os.environ[NAUTILUS_SCRIPT_SELECTED_FILE_PATHS].splitlines()
            if argument)
    except KeyError:
        BEFORE_EXIT_MESSAGE = EMPTY
    else:
        BEFORE_EXIT_MESSAGE = MSG_HIT_ENTER
    #
    if ARGUMENTS_LIST:
        for argument in ARGUMENTS_LIST:
            if os.path.isdir(argument):
                print_directory_tracklist(argument)
            else:
                print_file_tracklist(argument)
            #
        #
    else:
        print_directory_tracklist(os.getcwd())
    #
    if BEFORE_EXIT_MESSAGE:
        six.moves.input(BEFORE_EXIT_MESSAGE)
    sys.exit(RC_OK)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 ai expandtab syntax=python:

