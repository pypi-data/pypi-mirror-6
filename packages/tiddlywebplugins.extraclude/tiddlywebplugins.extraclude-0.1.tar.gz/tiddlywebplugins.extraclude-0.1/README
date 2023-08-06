[TiddlyWeb](http://tiddlyweb.com/) plugin that uses a validator
to process extraclusions.

# Intro

An extraclusion is markup in renderable wikitext which extracts
the contained text to a tiddler of its own. For example if the
following text were put as tiddler "foo":

    # Header

    Some text

    .extraclude bar

    ## Other Header

    Other text

    .extraclude

    # Another Header

    Hi!

The result would be two tiddlers in the same bag, "foo" and "bar".
"foo" would contain markup to trainsclude "bar".

The extracluded tiddlers inherits the `type` of the parent.

# Install

Install the Python package with:

    pip install -U tiddlywepblugins.extraclude


Add the package to `system_plugins` in `tiddlywebconfig.py`:

    config = {
        'system_plugins': ['tiddlywebplugins.extraclude']
    }

Copyright 2014 Peermore Limited
BSD License
