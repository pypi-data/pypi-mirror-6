"""
Process extraclusions on PUT of a single Tiddler.

Tiddler validation happens after bag policy checks
so we know we can write.

As long as this validator is late in the stack of
validators, other, security related, validators will
operate on the extraclude text.
"""

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import StoreError
from tiddlyweb.util import renderable
from tiddlyweb.web.validator import TIDDLER_VALIDATORS

import re


EXTRACLUDE_RE = re.compile(r'^.extraclude (.+?)\s*$([\s\S]*?)^.extraclude$',
        re.MULTILINE)

EXTRACLUDE_TYPEMAP = {
    'text/x-markdown': '{{%s}}',
    'text/x-tiddlywiki': '<<tiddler [[%s]]>>',
}

def process_extraclusion(tiddler, environ):
    """
    If the tiddler is renderable, look for
    extraclusions and process.
    """
    # return as quickly as possible if we don't need
    if not renderable(tiddler, environ):
        return
    if '.extraclude' not in tiddler.text:
        return
    store = environ['tiddlyweb.store']
    # ensure sane line endings. This might be happening elsewhere
    # but we need to be _sure_.
    text = tiddler.text.replace('\r', '')

    def replace(match):
        name = match.group(1)
        extract = match.group(2)
        new_tiddler = Tiddler(name, tiddler.bag)
        new_tiddler.type = tiddler.type
        new_tiddler.text = extract
        new_tiddler.modifier = tiddler.modifier
        new_tiddler.modified = tiddler.modified
        store.put(new_tiddler)
        return EXTRACLUDE_TYPEMAP[tiddler.type] % name

    try:
        text = EXTRACLUDE_RE.sub(replace, text)
    except StoreError:
        # bail out we could store, so don't update this tiddler
        return

    tiddler.text = text


def init(config):
    TIDDLER_VALIDATORS.append(process_extraclusion)
