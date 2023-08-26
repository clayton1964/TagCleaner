PLUGIN_NAME = "Clayton's Test Plugin"
PLUGIN_AUTHOR = "Clayton Mattatall"
PLUGIN_DESCRIPTION = "This plugin is an example"
PLUGIN_VERSION = '0.01'
PLUGIN_API_VERSIONS = ['2.2']
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"
PLUGIN_USER_GUIDE_URL = "https://my.program.site.org/example_plugin_documentation.html"

import json
import os
import ctypes  # An included library with Python install.

from picard import config, log
from picard.metadata import (register_album_metadata_processor, register_track_metadata_processor)
from picard.plugin import PluginPriority


file_to_write = os.path.join(config.setting["move_files_to"], "data_dump.txt")


def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def write_line(line_type, object_to_write, dump_json=False, append=True):
    file_mode = 'a' if append else 'w'
    try:
        with open(file_to_write, file_mode, encoding="UTF-8") as f:
            if dump_json:
                f.write('{0} JSON dump follows:\n'.format(line_type, ))
                f.write('{0}\n\n'.format(json.dumps(object_to_write, indent=4)))
            else:
                f.write("{0:s}: {1:s}\n".format(line_type, str(object_to_write), ))
    except Exception as ex:
        log.error("{0}: Error: {1}".format(PLUGIN_NAME, ex, ))


def dump_release_info(album, metadata, release):
    Mbox('Release Info', 'dump_release_info', 1)
    write_line('Release Argument 1 (album)', album, append=False)
    write_line('Release Argument 3 (release)', release, dump_json=True)


def dump_track_info(album, metadata, track, release):
    Mbox('Track Info', 'dump_track_info', 1)
    write_line('Track Argument 1 (album)', album)
    write_line('Track Argument 3 (track)', track, dump_json=True)
    write_line('Track Argument 4 (release)', release, dump_json=True)


# Register the plugin to run at a HIGH priority so that other plugins will
# not have an opportunity to modify the contents of the metadata provided.
register_album_metadata_processor(dump_release_info, priority=PluginPriority.HIGH)
register_track_metadata_processor(dump_track_info, priority=PluginPriority.HIGH)
