=================
 Hidden Original
=================

This plugin stashes away the original file, and uses a downsized one
as the `original` for mediagoblins purposes. The full size original is
available in the media entry field `hidden_original`.

The hidden original gets a non-guessable path (currently using
python's `uuid.uuid4()` to generate it). If you're using SSL, this
should keep your original files well hidden.

This plugin is licensed under the GNU APGL v3+.

Currently requires a patched mediagoblin to make it run image
preprocessing hooks, check out branch `stock` of
https://gitorious.org/mediagoblin-stock/mediagoblin

Installation
============

If you've checked out this plugin and mediagoblin in the same parent
directory, you should be able to build and install with

    ../mediagoblin/bin/python setup.py build
    ../mediagoblin/bin/python setup.py install

Tests
=====

After installing, run the built-in unit tests by invoking `python2
setup.py test` in the root directory. The tests require an installed
version of GNU MediaGoblin to be available for importing. If you've
checked out this plugin and mediagoblin in the same parent directory,
you should be able to run

    ../mediagoblin/bin/python setup.py test

TODO
====

- Functions to re-create the secret urls (mv the file from the old
  secret url to a new randomly created one). One function for a
  particular entry, one that does it for all of them.

- *Long term*: The hidden original should probably be completely
  inaccessible by default (in some "private_storage"?); and there
  should be a function `reveal_hidden(entry)` which makes the original
  accessible through some secret url for sharing that original, and
  another function `revoke_revelation(secret_url)` to revoke a
  particular share. One entry should be able to have several such
  published secret urls, so a user can share with otheruser1 and
  otheruser2, one url each, and then e.g. revoke the first url without
  the second one being revoked as well.
