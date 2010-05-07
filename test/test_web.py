"""
tests for visiting custom urls over the web
"""
from setup_test import setup_store, setup_web, BAGS
from tiddlywebplugins.urls.twanager import url
from tiddlywebplugins.urls import init as urls_init

from tiddlyweb.config import config
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.serializer import Serializer

import httplib2

BAGS.append('urls')

config['system_plugins'] = ['tiddlywebplugins.urls']

def test_load_url_single():
    """
    visit a single tiddler at a custom url
    """
    store = setup_store()
    url(['/foo', '/bags/foo/tiddlers/bar.json'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler('bar', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    response, content = http.request('http://test_domain:8001/foo')

    assert response.status == 200

    direct_url = http.request('http://test_domain:8001/bags/foo/tiddlers/bar.json')[1]
    assert content == direct_url

def test_refresh_urls():
    """
    register a url after the server has been started, and then refresh them
    """
    store = setup_store()
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler('bar', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    #check that no url exists yet
    response = http.request('http://test_domain:8001/foo')[0]
    assert response.status == 404

    url(['/foo', '/bags/foo/tiddlers/bar'])

    #resfresh the currently loaded set of urls
    response = http.request('http://test_domain:8001/urls/refresh')[0]
    assert response.status == 200

    #now check it was loaded successfully
    response = http.request('http://test_domain:8001/foo')[0]
    assert response.status == 200

def test_load_url_collection():
    """
    visit a collection of tiddlers at a custom url
    """
    store = setup_store()
    url(['/foo', '/bags/foo/tiddlers.json'])
    urls_init(config)
    setup_web()
    http = httplib2.Http()

    tiddler = Tiddler('bar', 'foo')
    tiddler.text = 'foo bar'
    store.put(tiddler)

    response, content = http.request('http://test_domain:8001/foo')

    assert response.status == 200

    direct_url = http.request('http://test_domain:8001/bags/foo/tiddlers.json')[1]
    assert content == direct_url
