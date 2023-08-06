from pywb.utils.wbexception import WbException
from pywb.utils.loaders import load_yaml_config

from wbexceptions import NotFoundException, InternalRedirect
from wbrequestresponse import WbResponse, StatusAndHeaders


import os
import logging


DEFAULT_PORT = 8080

#=================================================================
# adapted from wsgiref.request_uri, but doesn't include domain name
# and allows all characters which are allowed in the path segment
# according to: http://tools.ietf.org/html/rfc3986#section-3.3
# explained here:
# http://stackoverflow.com/questions/4669692/
#   valid-characters-for-directory-part-of-a-url-for-short-links


def rel_request_uri(environ, include_query=1):
    """
    Return the requested path, optionally including the query string

    # Simple test:
    >>> rel_request_uri({'PATH_INFO': '/web/example.com'})
    '/web/example.com'

    # Test all unecoded special chars and double-quote
    # (double-quote must be encoded but not single quote)
    >>> rel_request_uri({'PATH_INFO': "/web/example.com/0~!+$&'()*+,;=:\\\""})
    "/web/example.com/0~!+$&'()*+,;=:%22"
    """
    from urllib import quote
    url = quote(environ.get('PATH_INFO', ''), safe='/~!$&\'()*+,;=:@')
    if include_query and environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']

    return url


#=================================================================
class WSGIApp(object):
    def __init__(self, wb_router):
        self.wb_router = wb_router
        self.port = DEFAULT_PORT
        if hasattr(wb_router, 'port'):
            self.port = wb_router.port

    # Top-level wsgi application
    def __call__(self, env, start_response):
        if env.get('SCRIPT_NAME') or not env.get('REQUEST_URI'):
            env['REL_REQUEST_URI'] = rel_request_uri(env)
        else:
            env['REL_REQUEST_URI'] = env['REQUEST_URI']

        wb_router = self.wb_router
        response = None

        try:
            response = wb_router(env)

            if not response:
                msg = 'No handler for "{0}"'.format(env['REL_REQUEST_URI'])
                raise NotFoundException(msg)

        except InternalRedirect as ir:
            response = WbResponse(StatusAndHeaders(ir.status, ir.httpHeaders))

        except WbException as e:
            response = handle_exception(env, wb_router, e, False)

        except Exception as e:
            response = handle_exception(env, wb_router, e, True)

        return response(env, start_response)


#=================================================================
def handle_exception(env, wb_router, exc, print_trace):
    error_view = None
    if hasattr(wb_router, 'error_view'):
        error_view = wb_router.error_view

    if hasattr(exc, 'status'):
        status = exc.status()
    else:
        status = '400 Bad Request'

    if print_trace:
        import traceback
        err_details = traceback.format_exc(exc)
        print err_details
    else:
        logging.info(str(exc))
        err_details = None

    if error_view:
        import traceback
        return error_view.render_response(err_msg=str(exc),
                                          err_details=err_details,
                                          status=status)
    else:
        return WbResponse.text_response(status + ' Error: ' + str(exc),
                                        status=status)

#=================================================================
DEFAULT_CONFIG_FILE = 'config.yaml'


#=================================================================
def init_app(init_func, load_yaml=True, config_file=None):
    logging.basicConfig(format='%(asctime)s: [%(levelname)s]: %(message)s',
                        level=logging.DEBUG)
    logging.debug('')

    if load_yaml:
        if not config_file:
            config_file = os.environ.get('PYWB_CONFIG_FILE')
        if not config_file:
            config_file = DEFAULT_CONFIG_FILE

        config = load_yaml_config(config_file)

    try:
        if load_yaml:
            wb_router = init_func(config)
        else:
            wb_router = init_func()
    except:
        msg = '*** pywb app init FAILED config from "%s"!\n'
        logging.exception(msg, init_func.__name__)
        raise
    else:
        msg = '*** pywb app inited with config from "%s"!\n'
        logging.debug(msg, init_func.__name__)

    return WSGIApp(wb_router)


#=================================================================
def start_wsgi_server(the_app, name):  # pragma: no cover
    from wsgiref.simple_server import make_server
    from optparse import OptionParser

    opt = OptionParser('%prog [OPTIONS]')
    opt.add_option('-p', '--port', type='int', default=None)

    options, args = opt.parse_args()

    port = options.port

    if not port:
        port = the_app.port

    if not port:
        port = DEFAULT_PORT

    logging.info('Starting %s on port %s', name, port)

    try:
        httpd = make_server('', port, the_app)
        httpd.serve_forever()
    except KeyboardInterrupt as ex:
        pass
    finally:
        logging.info('Stopping %s', name)
