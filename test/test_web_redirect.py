"""
tests that involve redirects to separate websites
"""
from setup_test import setup_store, setup_web, BAGS
from tiddlywebplugins.urls.twanager import url
from tiddlywebplugins.urls import init as urls_init

from tiddlyweb.config import config

import httplib2

BAGS.append('urls')

config['system_plugins'] = ['tiddlywebplugins.urls']

def test_redirect_with_protocol():
    """
    add a redirect with a named protocol
    """
    store = setup_store()
    url(['/foo', 'http://www.google.com'])
    urls_init(config)
    setup_web()
    http =  httplib2.Http()

    http.follow_redirects = False
    response = http.request('http://test_domain:8001/foo')[0]
    assert response.status == 301
    assert response['location'] == 'http://www.google.com'

def test_redirect_with_www():
    """
    add a redirect without a protocol
    """
    store = setup_store()
    url(['/foo', 'www.google.com'])
    urls_init(config)
    setup_web()
    http =  httplib2.Http()

    http.follow_redirects = False
    response = http.request('http://test_domain:8001/foo')[0]
    assert response.status == 301
    assert response['location'] == 'http://www.google.com'

def test_redirect_with_tag():
    """
    add a redirect defined by tagging 'redirect'
    """
    store = setup_store()
    url(['--redirect', '/foo', '/bags'])
    urls_init(config)
    setup_web()
    http =  httplib2.Http()

    http.follow_redirects = False
    response = http.request('http://test_domain:8001/foo')[0]
    assert response.status == 301
    assert response['location'] == '/bags'
