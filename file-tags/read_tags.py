#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Read audio tags from local files.
Print a list of track number, artist, song title and duration,
suitable for pasting into Musicbrainz’ track parser.

Copyright (C) 2015 Rainer Schwarzbach <rainer@blackstream.de>
"""

import argparse
import glob
import logging
import os
import re
import sys
import taglib


__version__ = '0.1'


ALL_FILES = '*.*'
EMPTY = ''
FS_AUDIO_LENGTH = u'{0:02d}:{1:02d}'
FS_TRACK = u'{0[TRACKNUMBER]}. {0[ARTIST]} – {0[TITLE]} ({0[length]})'
LOG_MESSAGE_FORMAT = '%(levelname)-8s | %(message)s'
MISSING_TAG = u'(…)'
MSG_FILE_TAGS_MISSING = 'File {0!r}: Tags missing {1}'
PRX_TRACKS_TOTAL = re.compile(r'/.*')
SEPARATOR = u' / '
TAG_TRACK_NUMBER = 'TRACKNUMBER'
TAG_ARTIST = 'ARTIST'
TAG_TITLE = 'TITLE'
TAG_LENGTH = 'length'
REQUIRED_TAGS = (TAG_TRACK_NUMBER, TAG_ARTIST, TAG_TITLE)


def audio_length(seconds):
    """Return audio length in seconds as a mm:ss string"""
    _minutes, _seconds = divmod(int(seconds), 60)
    return FS_AUDIO_LENGTH.format(_minutes, _seconds)


def output_directory_tracklist(given_directory):
    """Output a tracklist from all files in the given directory.
    Files will be sorted by name before.
    """
    for single_file in sorted(glob.glob(os.path.join(given_directory,
                                                     ALL_FILES))):
        output_file_tracklist(single_file)
    #


def output_file_tracklist(given_file):
    """Output the file’s audio data as a tracklist line"""
    try:
        current_file = taglib.File(given_file)
    except OSError as os_error:
        # File types the taglib cannot handle will produce an OSError
        logging.error(os_error)
    else:
        current_tags = {}
        missing_tags = []
        for tag in REQUIRED_TAGS:
            try:
                current_tags[tag] = current_file.tags[tag][:]
            except KeyError:
                current_tags[tag] = MISSING_TAG
                missing_tags.append(tag)
            else:
                if tag == TAG_TRACK_NUMBER:
                    current_tags[tag] = PRX_TRACKS_TOTAL.sub(
                        EMPTY, current_tags[tag][0])
                else:
                    current_tags[tag] = SEPARATOR.join(current_tags[tag])
                #
            #
        try:
            current_tags[TAG_LENGTH] = audio_length(current_file.length)
        except AttributeError:
            current_tags[TAG_LENGTH] = u'…'
            missing_tags.append(TAG_LENGTH)
        if missing_tags:
            logging.warning(MSG_FILE_TAGS_MISSING.format(given_file,
                                                         missing_tags))
        print(FS_TRACK.format(current_tags))
    #


if __name__ == '__main__':
    # If no argument was given, process the current directory.
    # Else process the specified files or directories
    logging.basicConfig(format=LOG_MESSAGE_FORMAT, level=logging.DEBUG)
    ARGUMENT_PARSER = argparse.ArgumentParser(
        description=u'Read audio tags from local files and print them'
        ' as a tracklist suitable for the Musicbrainz track parser')
    ARGUMENT_PARSER.add_argument('file_or_directory',
                                 help='Files or directories to read'
                                 ' audio tags from',
                                 nargs='*')
    ARGUMENTS_LIST = ARGUMENT_PARSER.parse_args().file_or_directory
    if ARGUMENTS_LIST:
        for argument in ARGUMENTS_LIST:
            if os.path.isdir(argument):
                output_directory_tracklist(argument)
            else:
                output_file_tracklist(argument)
            #
        #
    else:
        output_directory_tracklist(os.getcwd())
    #
    sys.exit(0)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 expandtab autoindent syntax=python:

