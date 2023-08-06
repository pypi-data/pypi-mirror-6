"""
Test the validator.
"""

import shutil

from tiddlywebplugins.extraclude import process_extraclusion

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from tiddlywebplugins.utils import get_store


def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass

    config['wikitext.type_render_map'] = {
        'text/x-markdown': 'tiddlywebplugins.markdown',
        'text/x-tiddlywiki': 'stub'
    }

    store = get_store(config)
    module.store = store
    environ = {
        'tiddlyweb.config': config,
        'tiddlyweb.store': store,
    }
    module.environ = environ


def test_one_extraclusion():
    bag = Bag('bagone')
    store.put(bag)
    tiddler = Tiddler('one', 'bagone')
    tiddler.type = 'text/x-markdown'

    tiddler.text = """
# Header One

.extraclude two

# Header Two

Hi!

.extraclude

Bye!
"""
    process_extraclusion(tiddler, environ)

    assert '# Header Two' not in tiddler.text
    assert '{{two}}' in tiddler.text
    assert 'Hi!' not in tiddler.text

    two = store.get(Tiddler('two', 'bagone'))
    assert 'Hi' in two.text


def test_multi_extraclusion():
    tiddler = Tiddler('three', 'bagone')
    tiddler.type = 'text/x-tiddlywiki'
    tiddler.text = """
! Header One

.extraclude four

! Header Two

Hi!

.extraclude

.extraclude five

! Header Three

Bye!

.extraclude

end
"""
    process_extraclusion(tiddler, environ)

    assert '! Header Two' not in tiddler.text
    assert '<<tiddler [[four]]>>' in tiddler.text
    assert 'Hi!' not in tiddler.text

    assert '! Header Three' not in tiddler.text
    assert '<<tiddler [[five]]>>' in tiddler.text
    assert 'Bye!' not in tiddler.text
    assert 'end' in tiddler.text

    four = store.get(Tiddler('four', 'bagone'))
    assert 'Hi!' in four.text
    assert '! Header Two' in four.text
    assert '! Header Three' not in four.text
    five = store.get(Tiddler('five', 'bagone'))
    assert '! Header Three' in five.text
    assert '! Header Two' not in five.text
    assert 'Bye!' in five.text
