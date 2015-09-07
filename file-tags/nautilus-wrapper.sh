#!/bin/bash
#
# Thin wrapper around read_tags.py executing that script in a new
# gnome-terminal window using Python 3 as interpreter.
# This script can be symlinked from the 
#   ~/.local/share/nautilus/scripts/
# directory to enable Nautilus script integration for read_tags.py
#
# Copyright (C) 2015 Rainer Schwarzbach
#                    <blackstream-x@users.noreply.github.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

TERMINAL_TITLE="Tracklist"
PYTHON_EXECUTABLE="$(which python3)"
SCRIPT_DIRECTORY="$(dirname "$(readlink -f "$0")")"
WRAPPED_SCRIPT="read_tags.py"

/usr/bin/gnome-terminal \
    --title="${TERMINAL_TITLE}" \
    -e "${PYTHON_EXECUTABLE} ${SCRIPT_DIRECTORY}/${WRAPPED_SCRIPT}"

# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 expandtab autoindent syntax=sh:

