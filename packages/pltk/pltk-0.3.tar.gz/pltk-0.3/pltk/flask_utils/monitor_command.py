"""
Script for running a regular nose test which uses the Werkzeug test client as a
monitoring command against any remote server.
"""
import werkzeug.test as wtest
try:
    from urllib.request import http
except ImportError:
    import urllib2 as http
import nose


# defaults
host = '127.0.0.1'
scheme = 'http'
port = '5000'
prefix = ''


def mocked_run_app(app, environ, buffered=False):
    """Run the app with mocking."""
    if environ['HTTP_HOST'] == 'localhost':
        environ['HTTP_HOST'] = host
        environ['wsgi.url_scheme'] = scheme
        environ['SERVER_PORT'] = port

        if environ['PATH_INFO'].startswith('/0.1'):
            environ['PATH_INFO'] = prefix + environ['PATH_INFO']

    url = ''.join((environ['wsgi.url_scheme'],
                   '://',
                   environ['HTTP_HOST'],
                   ':',
                   environ['SERVER_PORT'],
                   environ['PATH_INFO']))
    if environ['QUERY_STRING']:
        url += '/?' + environ['QUERY_STRING']

    data = None

    if environ['REQUEST_METHOD'] == 'POST':
        data = environ['wsgi.input'].read()

    headers = {}
    for k in environ.keys():
        if k.lower().startswith('http_'):
            key = k[5:]
            key = key.replace('_', '-').lower()
            key = key[0].upper() + key[1:]
            for i in range(1, len(key)):
                if key[i - 1] == '-':
                    key = key[0:i] + key[i].upper() + key[i + 1:]
            headers[key] = environ[k]

    request = http.Request(url, data=data, headers=headers)
    try:
        handle = http.urlopen(request)
    except http.HTTPError as e:
        return ([x for x in e],
                str(e.code) + ' ' + e.msg,
                zip(e.headers.keys(), e.headers.values()))

    return ([x for x in handle],
            str(handle.getcode()) + ' ' + handle.msg,
            handle.headers.items())


def main(test_name, host_, scheme_, port_, prefix_):
    """The main entry point."""
    global host, scheme, port, prefix
    host = host_
    scheme = scheme_
    port = port_
    prefix = prefix_
    original_run_app = wtest.run_wsgi_app
    wtest.run_wsgi_app = mocked_run_app
    nose.main(argv=['nosetests', test_name])
    wtest.run_wsgi_app = original_run_app
