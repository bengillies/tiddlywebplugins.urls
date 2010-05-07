"""
tests that pass variables between source and destination in some way
"""
from setup_test import setup_store, setup_web, BAGS
from tiddlywebplugins.urls.twanager import url
from tiddlywebplugins.urls import init as urls_init

from tiddlyweb.config import config
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe

import httplib2

BAGS.append('urls')

config['system_plugins'] = ['tiddlywebplugins.urls']

def test_replace_variables():
    """
    access a url with variables in the destination
    """
    store = setup_store()
    url(['/foo/{tiddler_name:segment}', '/bags/foo/tiddlers/{{ tiddler_name }}.json'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler('bar', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    response, content = http.request('http://test_domain:8001/foo/bar')

    assert response.status == 200

    direct_url = http.request('http://test_domain:8001/bags/foo/tiddlers/bar.json')[1]
    assert content == direct_url

def test_recipe_variables():
    """
    access a recipe with variables in it
    """
    store = setup_store()
    url(['/foo/{name:segment}', '/recipes/custom/tiddlers'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler('bar', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    recipe = Recipe('custom')
    recipe.set_recipe([('{{ name:bar }}', '')])
    store.put(recipe)

    response, content = http.request('http://test_domain:8001/foo/foo')

    assert response.status == 200

    direct_url = http.request('http://test_domain:8001/recipes/custom/tiddlers')[1]
    assert content != direct_url #accessing directly, the default bag should be used instead

    #now check that the correct bag was actually loaded)
    recipe.set_recipe([('foo', '')])
    store.put(recipe)
    direct_url = http.request('http://test_domain:8001/recipes/custom/tiddlers')[1]
    assert content == direct_url
