"""
test the twanager command
"""
from tiddlywebplugins.urls.validator import InvalidDestinationURL, InvalidSelectorURL
from setup_test import setup_store

from tiddlywebplugins.urls.twanager import url
from tiddlywebplugins.urls import init as urls_init
from tiddlyweb.store import NoTiddlerError, NoBagError
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.config import config

import urllib

def test_add_internal_url():
    """
    add an internal (ie - not mapped, redirected) url
    """
    store = setup_store()
    urls_init(config)
    
    url(['/foo', '/bags/foo/tiddlers'])
    
    tiddler = Tiddler('/foo', 'urls')
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise AssertionError('URL not put into store')
    except NoBagError:
        raise AssertionError('urls bag not created')
    
    assert tiddler.title == '/foo'
    assert tiddler.text == '/bags/foo/tiddlers'
    assert tiddler.tags == []

def test_add_external_url():
    """
    add an external (ie - always redirect) url
    """
    store = setup_store()
    urls_init(config)
    
    url(['/google', 'http://www.google.com'])
    
    tiddler = Tiddler('/google', 'urls')
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise AssertionError('URL not put into store')
    except NoBagError:
        raise AssertionError('urls bag not created')
    
    assert tiddler.title == '/google'
    assert tiddler.text == 'http://www.google.com'
    assert tiddler.tags == []

def test_add_interal_redirect():
    """
    add an internal url, but make it a redirect
    """
    store = setup_store()
    urls_init(config)
    
    url(['--redirect', '/foobar', '/recipes/foobar/tiddlers'])
    
    tiddler = Tiddler('/foobar', 'urls')
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise AssertionError('URL not put into store')
    except NoBagError:
        raise AssertionError('urls bag not created')
    
    assert tiddler.title == '/foobar'
    assert tiddler.text == '/recipes/foobar/tiddlers'
    assert tiddler.tags == ['redirect']

def test_add_patterned_url():
    """
    add a URL with variables inside it
    """
    store = setup_store()
    urls_init(config)

    url(['/foobar/{baz:segment}[/]', '/recipes/foobar/tiddlers'])

    tiddler = Tiddler('/foobar/{baz:segment}[/]', 'urls')
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise AssertionError('URL not put into store')

    assert tiddler.title == '/foobar/{baz:segment}[/]'
    assert tiddler.text == '/recipes/foobar/tiddlers'

def test_add_variable_destination_url():
    """
    add a url with a variable destination
    """
    store = setup_store()
    urls_init(config)

    url(['/foobar/{baz:segment}[/]', '/recipes/foobar/tiddlers/{{ baz }}'])

    tiddler = Tiddler('/foobar/{baz:segment}[/]', 'urls')
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise AssertionError('URL not put into store')

    assert tiddler.title == '/foobar/{baz:segment}[/]'
    assert tiddler.text == '/recipes/foobar/tiddlers/{{ baz }}'

def test_add_invalid_url():
    """
    add a url with a variable destination but no variable in source to make
    sure that it errors
    """
    store = setup_store()
    urls_init(config)

    #try and add a variable destination with no variable in the source
    try:
        url(['/foobar/baz/tada', '/recipes/{{ foobar }}/tiddlers/{{ baz }}'])
        raise AssertionError('Invalid URL put into store successfully')
    except InvalidDestinationURL:
        pass #success

    tiddler = Tiddler('/foobar/baz/tada', 'urls')
    try:
        store.get(tiddler)
        raise AssertionError('Invalid URL found in store')
    except NoTiddlerError:
        pass #success

def test_add_invalid_external_url():
    """
    add a URL that does not match any patterns
    ie - it is not internal, but not recognised as external
    """
    store = setup_store()
    urls_init(config)

    try:
        url(['/foo/bar/baz/', 'foo.bar.baz'])
        raise AssertionError('Invalid URL put into store successfully')
    except InvalidDestinationURL:
        pass #success

    tiddler = Tiddler('/foo/bar/baz/', 'urls')
    try:
        store.get(tiddler)
        raise AssertionError('Invalid URL found in store')
    except NoTiddlerError:
        pass #success

def test_add_invalid_internal_url():
    """
    add an internal URL for mapping to (ie - not redirecting) that is
    not supported by tiddlywebplugins.urls (which only supports tiddlers
    and collections of tiddlers
    """
    store = setup_store()
    urls_init(config)

    try:
        url(['/foo/bar/baz/', '/bags/foo'])
        raise AssertionError('Invalid URL put into store successfully')
    except InvalidDestinationURL:
        pass #success

    tiddler = Tiddler('/foo/bar/baz/', 'urls')
    try:
        store.get(tiddler)
        raise AssertionError('Invalid URL found in store')
    except NoTiddlerError:
        pass #success

def test_add_invalid_selector():
    """
    add an invalid selector path
    """
    store = setup_store()
    urls_init(config)

    try:
        url(['/invalid/{variable:unrecognisedtype}', 'www.google.com'])
        raise AssertionError('Invalid URL put into store successfully')
    except InvalidSelectorURL:
        pass #success

def test_add_unicode():
    """
    add some unicode
    """
    store = setup_store()
    urls_init(config)

    title = urllib.unquote(u'%2Funicode%2F%7E%7E%E2%88%82%C3%A5%C2%A8%5E%C3%A5%7E%C3%9F%E2%88%82%5E%C3%B8')
    text = urllib.unquote(u'/bags/%7E%7E%E2%88%82%C3%A5%C2%A8%5E%C3%A5%7E%C3%9F%E2%88%82%5E%C3%B8/tiddlers/%7E%7E%E2%88%82%C3%A5%C2%A8%5E%C3%A5%7E%C3%9F%E2%88%82%5E%C3%B8')
    print title, text
    url([title, text])

    tiddler = Tiddler(title, 'urls')
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise AssertionError(u'Unicode tiddler not in store')

    assert tiddler.title == title
    assert tiddler.text == text
