# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Clayton Mattatall (DarkOverLordII)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

PLUGIN_NAME = 'Tag Cleaner'
PLUGIN_AUTHOR = 'Clayton Mattatall'
PLUGIN_DESCRIPTION = '''
This plugin gives users the ability to sanitize the metadata in
individual files using bulk actions. All tags are scanned to 
locate those that match the entries defined in the plugin's 
configuration. If a match is found, the defined action is taken
and the current tag. 
<br /><br />
When this plugin is installed, a settings page will be added 
to Picard's options, which is where the plugin is configured.
<br /><br />
Please see the <a href="https://github.com/rdswift/picard-plugins/blob/2.0_RDS_Plugins/plugins/tag_cleaner/docs/README.md">user guide</a> on GitHub for more information.
'''
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['2.0', '2.1', '2.2', '2.3', '2.6', '2.7', '2.8']
PLUGIN_LICENSE = "GPL-2.0"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.txt"

import re

from picard import (
    config,
    log,
)
from picard.metadata import (
    MULTI_VALUED_JOINER,
    register_track_metadata_processor,
)
from picard.plugin import PluginPriority
from picard.plugins.tag_cleaner.ui_options_tag_cleaner import (
    Ui_Tag_CleanerOptionsPage,
)

from picard.ui.options import (
    OptionsPage,
    register_options_page,
)


pairs_split = re.compile(r"\r\n|\n\r|\n").split

OPT_MATCH_ENABLED = 'tag_cleaner_enabled'
OPT_MATCH_PAIRS = 'tag_cleaner_replacement_pairs'
OPT_MATCH_FIRST = 'tag_cleaner_apply_first_match_only'
OPT_MATCH_REGEX = 'tag_cleaner_use_regex'


class TagCleaner():
    pairs = []

    @classmethod
    def refresh(cls):
        log.debug("%s: Refreshing the tags to sanitize.",
            PLUGIN_NAME, 'RegEx' if config.Option.exists("setting", OPT_MATCH_REGEX) and config.setting[OPT_MATCH_REGEX] else 'Simple',)
        if not config.Option.exists("setting", OPT_MATCH_PAIRS):
            log.warning("%s: Unable to read the '%s' setting.", PLUGIN_NAME, OPT_MATCH_PAIRS,)
            return

        def _make_re(map_string):
            # Replace period with temporary placeholder character (newline)
            re_string = str(map_string).strip().replace('.', '\n')
            # Convert wildcard characters to regular expression equivalents
            re_string = re_string.replace('*', '.*').replace('?', '.')
            # Escape carat and dollar sign for regular expression
            re_string = re_string.replace('^', '\\^').replace('$', '\\$')
            # Replace temporary placeholder characters with escaped periods
            re_string = '^' + re_string.replace('\n', '\\.') + '$'
            # Return regular expression with carat and dollar sign to force match condition on full string
            return re_string

        cls.pairs = []
        for pair in pairs_split(config.setting[OPT_MATCH_PAIRS]):
            if "=" not in pair:
                continue
            original, replacement = pair.split('=', 1)
            original = original.strip()
            if not original:
                continue
            replacement = replacement.strip()
            cls.pairs.append((original if config.setting[OPT_MATCH_REGEX] else _make_re(original), replacement))
            log.debug('%s: Add genre mapping pair: "%s" = "%s"', PLUGIN_NAME, original, replacement,)
        if not cls.pairs:
            log.debug("%s: No genre replacement maps defined.", PLUGIN_NAME,)


class TagCleanerOptionsPage(OptionsPage):

    NAME = "tag_cleaner"
    TITLE = "Tag Cleaner"
    PARENT = "plugins"

    options = [
        config.TextOption("setting", OPT_MATCH_PAIRS, ''),
        config.BoolOption("setting", OPT_MATCH_FIRST, False),
        config.BoolOption("setting", OPT_MATCH_ENABLED, False),
        config.BoolOption("setting", OPT_MATCH_REGEX, False),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Tag_CleanerOptionsPage()
        self.ui.setupUi(self)

    def load(self):
        # Enable external link
        self.ui.format_description.setOpenExternalLinks(True)

        self.ui.tag_cleaner_replacement_pairs.setPlainText(config.setting[OPT_MATCH_PAIRS])
        self.ui.tag_cleaner_first_match_only.setChecked(config.setting[OPT_MATCH_FIRST])
        self.ui.cb_enable_tag_cleaner.setChecked(config.setting[OPT_MATCH_ENABLED])
        self.ui.cb_use_regex.setChecked(config.setting[OPT_MATCH_REGEX])

        self.ui.cb_enable_tag_cleaner.stateChanged.connect(self._set_enabled_state)
        self._set_enabled_state()

    def save(self):
        config.setting[OPT_MATCH_PAIRS] = self.ui.tag_cleaner_replacement_pairs.toPlainText()
        config.setting[OPT_MATCH_FIRST] = self.ui.tag_cleaner_first_match_only.isChecked()
        config.setting[OPT_MATCH_ENABLED] = self.ui.cb_enable_tag_cleaner.isChecked()
        config.setting[OPT_MATCH_REGEX] = self.ui.cb_use_regex.isChecked()

        TagCleaner.refresh()

    def _set_enabled_state(self, *args):
        self.ui.gm_replacement_pairs.setEnabled(self.ui.cb_enable_tag_cleaner.isChecked())


def track_tag_cleaner(album, metadata, *args):
    if not config.setting[OPT_MATCH_ENABLED]:
        return
    if 'genre' not in metadata or not metadata['genre']:
        log.debug("%s: No genres found for: \"%s\"", PLUGIN_NAME, metadata['title'],)
        return
    genres = set()
    metadata_genres = str(metadata['genre']).split(MULTI_VALUED_JOINER)
    for genre in metadata_genres:
        for (original, replacement) in TagCleaner.pairs:
            if genre and re.search(original, genre, re.IGNORECASE):
                genre = replacement
                if config.setting[OPT_MATCH_FIRST]:
                    break
        if genre:
            genres.add(genre.title())
    genres = sorted(genres)
    log.debug("{0}: Genres updated from {1} to {2}".format(PLUGIN_NAME, metadata_genres, genres,))
    metadata['genre'] = genres


# Register the plugin to run at a LOW priority.
register_track_metadata_processor(track_tag_cleaner, priority=PluginPriority.LOW)
register_options_page(TagCleanerOptionsPage)

TagCleaner.refresh()
