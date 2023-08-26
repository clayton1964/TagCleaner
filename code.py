PLUGIN_NAME = "Clayton's Test Plugin"
PLUGIN_AUTHOR = "Clayton Mattatall"
PLUGIN_DESCRIPTION = "This plugin is an example"
PLUGIN_VERSION = '0.001'
PLUGIN_API_VERSIONS = ['2.2']
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"
PLUGIN_USER_GUIDE_URL = "https://my.program.site.org/example_plugin_documentation.html"


# from picard.plugins import PluginInterface
from picard.metadata import register_track_metadata_processor
import re

def remove_tags(tagger, metadata, track, release):
    # Remove specific tags from metadata
    tags_to_remove = ["encodedby"]  # Add the tags you want to remove
    for tag in tags_to_remove:
        if tag in metadata:
            del metadata[tag]

    return metadata


# Register the plugin
# PLUGIN = RemoveTagsPlugin()

# Register the plugin to run at a HIGH priority so that other plugins will
# not have an opportunity to modify the contents of the metadata provided.
register_track_metadata_processor(remove_tags, priority=PluginPriority.HIGH)

