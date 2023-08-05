# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2014 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

try:
    from PIL import Image
except ImportError:
    import Image

import logging
from mediagoblin import mg_globals as mgg
from mediagoblin.processing import (BadMediaFail, store_public)
import uuid

PIL_FILTERS = {
    'NEAREST': Image.NEAREST,
    'BILINEAR': Image.BILINEAR,
    'BICUBIC': Image.BICUBIC,
    'ANTIALIAS': Image.ANTIALIAS}
# TODO: want to say this instead:
#from mediagoblin.media_types.image import PIL_FILTERS

__VERSION__ = '0.1.3+' # releases get numbers, post release a "+" appended
_log = logging.getLogger(__name__)

def setup_plugin():
    _log.info('Hidden Original plugin set up!')

def stash_original(processor, quality=None, filter=None):
    """This function creates a secret filename for storing the original
    media file and saves that path with the key "hidden_original",
    then downsizes the file (processor.process_filename) that
    eventually gets stored as "original".

    The `processor' argument is one of the CommonImageProcessors of
    media_types.image

    Note that since we downsize to the medium size, a separate
    'medium' entry will not be created in the regular image process
    function ('medium' versions are only created if the original is
    larger than the medium size).

    """
    if u"hidden_original" in processor.entry.media_files \
       and mgg.public_store.file_exists(
           processor.entry.media_files[u"hidden_original"]):
        # This should happen if we're called from Resizer instead of
        # InitialProcessor
        return

    # Stash away the actual original under the key "hidden_original".
    secret_filename = "%s-%s" % (uuid.uuid4(),
                                 processor.name_builder.fill('{basename}{ext}'))
    # uuid4() as in get_unique_filepath, good enough for our purposes.
    store_public(processor.entry,
                 u"hidden_original",
                 processor.process_filename,
                 secret_filename)

    # Downsize the faux original to the "medium" size:
    new_size = (mgg.global_config['media:' + 'medium']['max_width'],
                mgg.global_config['media:' + 'medium']['max_height'])

    # TODO: The following overlaps a bit with generate_thumb,
    # resize_image and resize_tool, but those functions do way too
    # much; e.g. storing metadata and the file itself.
    if not quality:
        quality = processor.image_config['quality']
    if not filter:
        filter = processor.image_config['resize_filter']
    try:
        im = Image.open(processor.process_filename)
    except IOError:
        raise BadMediaFail()
    if im.size[0] > new_size[0] or im.size[1] > new_size[1]:
        try:
            resize_filter = PIL_FILTERS[filter.upper()]
        except KeyError:
            raise Exception('Filter "{0}" not found, choose one of {1}'.format(
                unicode(filter),
                u', '.join(PIL_FILTERS.keys())))

        im.thumbnail(new_size, resize_filter)

        # Overwrite the process_filename file with our downsized version:
        with file(processor.process_filename, 'w') as resized_original:
            im.save(resized_original, quality=quality)
        # This will later get used as the "original" in copy_original

    # else:
    #     A small file, just keep the original as is.


hooks = {
    'setup': setup_plugin,
    'imageprocessor_preprocess': stash_original
    }
