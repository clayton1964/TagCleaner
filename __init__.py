# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Clayton Mattatall
#
# This program is free software; you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

PLUGIN_NAME = "Tag Cleaner"
PLUGIN_AUTHOR = "Clayton Mattatall"
PLUGIN_DESCRIPTION = """
Have you ever needed to totally erase/remove ALL metadata(tags) from your audio files?
What about correcting non-compliant metadata within audio files?
How about software, such as 'Station Playlist' that will write APEv2 tags with new data but completely ignores
the fact that it should update existing ID3 tags with the new data. This creates a total mess later since you
do NOT know which tags are the most up-to-date.
There are many apps out there that 'butcher' audio files when adding metadata to them. This includes such actions
as adding the wrong type of metadata frames to the respective audio files.

This plugin's aim is to perform different types of 'cleaning' on your files. This can be simply checking for
compliance to established standards, all the way to removing EVERY possible piece of metadata leaving you with
pure sound data and nothing else.
"""
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['2.2']
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-3.0.html"
PLUGIN_USER_GUIDE_URL = "https://github.com/clayton1964/TagCleaner/blob/master/README.md"

import json
import os

from picard import config, log
from picard.metadata import (register_album_metadata_processor,
                           register_track_metadata_processor)
from picard.plugin import PluginPriority

WIDGET_UPDATE_INTERVAL = 0.5

file_to_write = os.path.join(config.setting["move_files_to"], "data_dump.txt")

def write_line(line_type, object_to_write, dump_json=False, append=True):
    file_mode = 'a' if append else 'w'
    try:
        with open(file_to_write, file_mode, encoding="UTF-8") as f:
            if dump_json:
                f.write('{0} JSON dump follows:\n'.format(line_type,))
                f.write('{0}\n\n'.format(json.dumps(object_to_write, indent=4)))
            else:
                f.write("{0:s}: {1:s}\n".format(line_type, str(object_to_write),))
    except Exception as ex:
        log.error("{0}: Error: {1}".format(PLUGIN_NAME, ex,))

        
action_loader = ActionLoader()
action_runner = ActionRunner()
register_album_action(ExecuteAlbumActions())
register_track_action(ExecuteTrackActions())
register_options_page(PostTaggingActionsOptions)
