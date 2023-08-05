import os

import py.test

from tiddlyweb.config import config
from tiddlyweb.store import Store, NoBagError, NoUserError, NoRecipeError, NoTiddlerError

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User

from tiddlywebplugins.postgresql import Base

import simplejson

def setup_module(module):
    module.store = Store(
            config['server_store'][0],
            config['server_store'][1],
            {'tiddlyweb.config': config}
            )
# delete everything
    Base.metadata.drop_all()
    Base.metadata.create_all()
    import warnings
    warnings.simplefilter('error')


def test_tiddler_text():
    store.put(Bag('onebag'))
    tiddler = Tiddler('tid', 'onebag')

    tiddler.text=u"'|| from"
    store.put(tiddler)

    tiddler = store.get(tiddler)

    print tiddler.text
