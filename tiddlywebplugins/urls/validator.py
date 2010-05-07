"""
helper functions and classes
"""
from selector import SimpleParser
import urllib
import re

class InvalidDestinationURL(Exception):
    """
    This is raised when the URL given cannot be figured out.
    This is due to invalid syntax when inputting the url to
    map to.
    """
    pass

class InvalidSelectorURL(Exception):
    """
    This is raised when the Selector pattern is invalid
    """
    pass

class NoURLFoundError(Exception):
    """
    This shouldn't ever be raised in practise, as if we get 
    into this module, the url has already matched so should 
    match again. If you get this, there is a bug in the code 
    somewhere
    """
    pass

def is_redirect(tiddler):
    """
    determine whether the url is a redirect, or a mask
    for another tiddlyweb url
    
    return True/False
    """
    if 'redirect' in tiddler.tags:
        return True
    
    regex = '^(?:\w+:\/\/\/*)|www\.'
    if re.search(regex, tiddler.text):
        return True
    
    return False

def figure_destination(url_part):
    """
    Figure out where we are going.
    
    return bag/recipe/tiddler name and extension
    """
    regex = '^\/((?:recipes)|(?:bags))\/([^\/]+)\/tiddlers([^\?]+)?(?:\??.*)'
    result = {}
    
    matches = re.findall(regex, url_part)
    for match in matches:
        container_type, container_name, tiddler = match
        if container_type in ['recipes', 'bags']:
            result['%s_name' % container_type[:-1]] = container_name
        if tiddler:
            #split the tiddler to find the extension
            if tiddler.startswith('/'):
                #we have a tiddler name and optionally an extension
                tiddler_and_extension = tiddler[1:].rsplit('.', 1)
                result['tiddler_name'] = tiddler_and_extension[0]
                if len(tiddler_and_extension) == 2:
                    result['extension'] = tiddler_and_extension[1]
            elif tiddler.startswith('.'):
                #we just have an extension
                result['extension'] = tiddler[1:]
            
    if not result:
        raise InvalidDestinationURL('URL \'%s\' is incorrectly formatted' % \
            url_part)
    
    return result
 
def replace_url_patterns(replace_variables, url):
    """
    replace any variables specified in the desired url, with any
    patterns specified in selector.
    
    uses recipe like syntax (ie - /recipes/{{ foo }}/tiddlers)
    
    returns the new url
    """
    regex = '{{ ([^ }}]+) }}'
    destination_variables = re.findall(regex, url)

    for replace_name in destination_variables:
        try:
            url = url.replace('{{ %s }}' % replace_name, replace_variables[replace_name])
        except KeyError:
            raise InvalidDestinationURL('Variables present in destination url but not found in selector')

    return url

def validate_url(tiddler):
    """
    check the destination url and selector url to make sure they are valid
    """
    selector_url = tiddler.title
    destination_url = tiddler.text
    
    parser = SimpleParser()
    try:
        regex = parser.parse(selector_url)
        match = re.match(regex, selector_url)
        if match:
            selector_variables = dict((key, key) for key in match.groupdict().iterkeys())
        else:
            selector_variables = {}
    except KeyError:
        raise InvalidSelectorURL

    redirect = is_redirect(tiddler)
    destination_url = replace_url_patterns(selector_variables, destination_url)
    if not redirect:
        figure_destination(destination_url)

    return True
