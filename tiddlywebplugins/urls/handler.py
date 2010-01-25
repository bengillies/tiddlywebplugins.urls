"""
the main entry point for all urls
"""
from tiddlyweb.filters import parse_for_filters
from tiddlyweb.control import get_tiddlers_from_bag
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.handler.recipe import get_tiddlers as recipe_tiddlers
from tiddlyweb.web.handler.bag import get_tiddlers as bag_tiddlers
from tiddlyweb.web.handler.tiddler import get as tiddler_get

from tiddlywebplugins.utils import ensure_bag
import re


class NoURLFoundError(IOError):
    """
    This shouldn't ever be raised in practise, as if we get 
    into this module, the url has already matched so should 
    match again. If you get this, there is a bug in the code 
    somewhere
    """
    pass

class InvalidDestinationURL(IOError):
    """
    This is raised when the URL given cannot be figured out.
    This is due to invalid syntax when inputting the url to
    map to.
    """
    pass

def get_handler(environ, start_response):
    """
    selector comes to this function when a url is found. 
    
    retrieve the recipe/serialization details and pass to 
    tiddlyweb.web.handler.recipe.get_tiddlers
    """
    selector_variables = extract_variables(environ['wsgiorg.routing_args'][1])
    #add the username to be more compliant with recipe variables
    selector_variables['user'] = environ['tiddlyweb.usersign']['name']
    
    potential_matches = get_urls(environ['tiddlyweb.config']['url_bag'], environ['tiddlyweb.store'])
    match = match_url(environ['tiddlyweb.config']['selector'], environ['selector.matches'][0], potential_matches)
    
    destination_url = replace_url_patterns(selector_variables, match.text)
    
    if is_redirect(match):
        if destination_url.startswith('www.'):
            destination_url = 'http://' + destination_url
            
        if 'analytics' in match.tags:
            store_analytics(environ, environ['tiddlyweb.config']['analytics_names']['redirect_name'], match.title)
        #redirect to the url and return
        start_response('301 Moved Permanently', [
            ('Location', str(destination_url))
            ])
        return_link = '''<html>
<head>
<title>URL Redirect</title>
</head>
<body>
Please see <a href="%s">%s</a>
</body>
</html>''' % (destination_url, destination_url)
        return return_link
    
    try:
        url_part, custom_filters = destination_url.split('?', 1)
    except ValueError:
        url_part = destination_url
        custom_filters = None
    
    mime_type = 'default'
    destination_parts = figure_destination(url_part)
    for part, value in destination_parts.iteritems():
        if part == 'extension':
            mime_type = environ['tiddlyweb.config']['extension_types'].get(value, None)
        else:
            environ['wsgiorg.routing_args'][1][part] = str(value)
    
    destination_parts.update(selector_variables)
    environ['tiddlyweb.recipe_template'] = destination_parts
            
    filters = figure_filters(environ['tiddlyweb.filters'], custom_filters)
    environ['tiddlyweb.filters'] = filters
    
    #set tiddlyweb.type to make sure we call the correct serializer
    environ['tiddlyweb.type'] = [mime_type]
    
    core_handler = analyze_url(environ, destination_parts, match)
    
    return core_handler(environ, start_response)

def analyze_url(environ, destination_parts, match):
    """
    Figure out which function to call and return that function.
    
    Also, work out details for any analytics, if required
    """
    if 'recipe_name' in destination_parts:
        container_type = 'recipe_name'
    elif 'bag_name' in destination_part:
        container_type = 'bag_name'
    else:
        raise InvalidDestinationURL('URL \'%s\' is incorrectly formatted' % destination_url)
        
    tiddler_exists = 'tiddler_name' in destination_parts
        
    if 'analytics' in match.tags:
        #do analytics
        container_name = destination_parts[container_type]
        analytic_type = environ['tiddlyweb.config']['analytics_names'][container_type]
        if tiddler_exists:
            analytic_bag = '%s_%s' % (analytic_type, container_name)
        else:
            analytic_bag = analytic_type
        store_analytics(environ, analytic_bag, \
            destination_parts.get('tiddler_name', container_name))
    
    if tiddler_exists:
        return tiddler_get
    else:
        handler_funcs = {
            'recipe_name': recipe_tiddlers,
            'bag_name': bag_tiddlers
        }
        return handler_funcs[container_type]
        
def store_analytics(environ, analytic_bag, tiddler_name):
    """
    store some useful info about what has been requested
    and who has requested it
    """
    tiddler = Tiddler(tiddler_name)
    tiddler.bag = analytic_bag
    tiddler.fields['REMOTE_ADDR'] = environ['REMOTE_ADDR']
    tiddler.fields['SCRIPT_NAME'] = environ['SCRIPT_NAME']
    tiddler.fields['HTTP_USER_AGENT'] = environ['HTTP_USER_AGENT']
    tiddler.fields['QUERY_STRING'] = environ.get('QUERY_STRING', '')
    
    tiddler.text = 'User at "%s" accessed "%s" with Agent "%s". ' \
        'Query String was "%s"' % \
        (environ['REMOTE_ADDR'], environ['SCRIPT_NAME'], \
        environ['HTTP_USER_AGENT'], environ.get('QUERY_STRING', ''))
    
    ensure_bag(analytic_bag, environ['tiddlyweb.store'], \
        environ['tiddlyweb.config']['analytics_policy'], \
        environ['tiddlyweb.config']['analytics_description'])
    environ['tiddlyweb.store'].put(tiddler)

def match_url(selector, url, potential_matches):
    """
    match the current url with the correct url in the url_bag
    
    return a tuple of (selector_path, destination_url)
    """
    for tiddler in potential_matches:
        #turn the selector path into the same regex that will appear in selector.matches
        url_regex = selector.parser.__call__(tiddler.title)
        if re.search(url_regex, url):
            #we have found our url
            return tiddler
    raise NoURLFoundError('URL not found in selector')

def get_urls(url_bag, store):
    """
    retrieve a list of selector/destination pairs based
    on the tiddlers in the url bag
    """
    bag = Bag(url_bag)
    bag = store.get(bag)
    tiddlers = get_tiddlers_from_bag(bag)
    return (tiddler for tiddler in tiddlers)

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

def figure_filters(filters, custom_filters):
    """
    figure out the filters that have been added to the query
    string and match them with filters in the destination. 
    
    Override any that match.
    
    return a list of filter functions
    """
    if custom_filters:
        custom_filters = parse_for_filters(custom_filters)[0]
        #strip duplicate filters
        result_filters = [custom_filter for custom_filter in custom_filters if custom_filter[1][0] not in [user_filter[1][0] for user_filter in filters]]
        if len(filters) > 0:
            result_filters.extend(filters)
        return result_filters
    return filters

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
                tiddler_and_extension = tiddler[1:].rsplit('.',1)
                result['tiddler_name'] = tiddler_and_extension[0]
                if len(tiddler_and_extension) == 2:
                    result['extension'] = tiddler_and_extension[1]
            elif tiddler.startswith('.'):
                #we just have an extension
                result['extension'] = tiddler[1:]
            
    if not result:
        raise InvalidDestinationURL('URL \'%s\' is incorrectly formatted' % url_part)
    
    return result
    

def extract_variables(routing_args):
    """
    extract wsgiorg.routing_args and set as appropriate
    
    returns a dict of all variables found
    """
    variables = {}
    
    if routing_args:
        for element, value in routing_args.iteritems():
            variables[element] = value
            
    return variables

def replace_url_patterns(replace_variables, url):
    """
    replace any variables specified in the desired url, with any
    patterns specified in selector.
    
    uses recipe like syntax (ie - /recipes/{{ foo }}/tiddlers)
    
    returns the new url
    """
    for index, value in replace_variables.iteritems():
        if value is not None:
            url = url.replace('{{ %s }}' % index, value)
    
    return url
