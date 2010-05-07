# -*- encoding: UTF-8 -*-
"""
tests that deal with unicode and spaces
"""
from setup_test import setup_store, setup_web, BAGS
from tiddlywebplugins.urls.twanager import url
from tiddlywebplugins.urls import init as urls_init

from tiddlyweb.config import config
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag

import httplib2
from urllib import quote

BAGS.append('urls')

config['system_plugins'] = ['tiddlywebplugins.urls']

def test_spaces():
    """
    visit a url destination with spaces
    """
    store = setup_store()
    url(['/foo', '/bags/foo/tiddlers/bar baz.json'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler('bar baz', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    response, content = http.request('http://test_domain:8001/foo')

    assert response.status == 200

    direct_url = http.request('http://test_domain:8001/bags/foo/tiddlers/bar%20baz.json')[1]
    assert content == direct_url

def test_spaces_in_variables():
    """
    visit a url by passing a variable with spaces into the destination
    """
    store = setup_store()
    url(['/foo/{bar:segment}', '/bags/foo/tiddlers/{{ bar }}.json'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler('bar baz', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    response, content = http.request('http://test_domain:8001/foo/bar%20baz')

    assert response.status == 200

    direct_url = http.request('http://test_domain:8001/bags/foo/tiddlers/bar%20baz.json')[1]
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

    tiddler = Tiddler('bar baz', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    tiddler = Tiddler('default', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    recipe = Recipe('custom')
    recipe.set_recipe([('foo', 'select=title:{{ name:default }}')])
    store.put(recipe)

    response, content = http.request('http://test_domain:8001/foo/bar%20baz')

    assert response.status == 200

    direct_url = http.request('http://test_domain:8001/recipes/custom/tiddlers')[1]
    assert content != direct_url #accessing directly, the default tiddler should be used instead

    #now check that the correct bag was actually loaded)
    recipe.set_recipe([('foo', 'select=title:bar%20baz')])
    store.put(recipe)
    direct_url = http.request('http://test_domain:8001/recipes/custom/tiddlers')[1]
    assert content == direct_url

def test_unicode():
    """
    visit a url destination with unicode
    """
    store = setup_store()
    url(['/foo', u'/bags/foo/tiddlers/bar œ∑´®†¥.json'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler(u'bar œ∑´®†¥', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    response, content = http.request('http://test_domain:8001/foo')

    assert response.status == 200

    direct_url = http.request(u'http://test_domain:8001/bags/foo/tiddlers/bar%20œ∑´®†¥.json')[1]
    assert content == direct_url

def test_unicode_in_variables():
    """
    visit a url by passing a variable with spaces into the destination
    """
    store = setup_store()
    url(['/foo/{bar:segment}', '/bags/foo/tiddlers/{{ bar }}.json'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler(u'bar œ∑´®†¥', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    response, content = http.request(u'http://test_domain:8001/foo/bar%20œ∑´®†¥')

    assert response.status == 200

    direct_url = http.request(u'http://test_domain:8001/bags/foo/tiddlers/bar%20œ∑´®†¥.json')[1]
    assert content == direct_url

def test_unicode_in_recipes():
    """
    visit a recipe passing unicode in as one of the variables
    """
    store = setup_store()
    url(['/foo/{bar:segment}', '/recipes/custom/tiddlers'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    bag = Bag(u'unicodeø•º∆∆˙ª')
    store.put(bag)
    tiddler = Tiddler(u'bar œ∑´®†¥', u'unicodeø•º∆∆˙ª')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    recipe = Recipe('custom')
    recipe.set_recipe([('{{ bar:foo }}', '')])
    store.put(recipe)

    response, content = http.request('http://test_domain:8001/foo/unicodeø•º∆∆˙ª')

    assert response.status == 200

    direct_url = http.request(u'http://test_domain:8001/recipes/custom/tiddlers')[1]
    assert content != direct_url #direct_url should load the foo bag instead

    recipe.set_recipe([(u'unicodeø•º∆∆˙ª', '')])
    store.put(recipe)
    direct_url = http.request(u'http://test_domain:8001/recipes/custom/tiddlers')[1]
    assert content == direct_url
