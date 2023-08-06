pltk: Paylogic toolkit
======================

The ``pltk`` package is a collection of useful tools for frameworks and other tools. At the moment there's only one
set of them - flask related tools.

.. image:: https://api.travis-ci.org/paylogic/pltk.png
   :target: https://travis-ci.org/paylogic/pltk
.. image:: https://pypip.in/v/pltk/badge.png
   :target: https://crate.io/packages/pltk/
.. image:: https://coveralls.io/repos/paylogic/pltk/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/pltk


Installation
------------

.. sourcecode::

    pip install pltk


Usage
-----

Package contains several utility modules. We will describe them one by one.


Useful Flask commands
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pltk import commands
    commands.install_commands(app, manager, db, model_collector)

then your app will have such additional commands:

    monitor_test
        Run a test as monitor command.
        Example usage::

            $ app monitor_test \
               -T app.tests.test_utils:TestView \
               -H dev.app.com -P 443 -R /unstable -S https

    shell
        Run Python shell with application context.

    dbshell
        Run database shell.

    http
        Run HTTP emulating console.
        Examples::
            - POST /foo/bar list=[1,2,3,4]
            - POST /user/login email=a@b.com password=p
            - GET /user/profile
            - header Authorization 1232123123

    print_settings
        Print all current Flask Settings.

    ec2_backup
        Create an ami from the current server and pushes its contents to s3.

    compile_messages
        Update the gettext messages.pot file and initialize the supported languages (if not already)
        and compile the messages to .mo files.
        This command assumes it is executed from the root of the project and stores translations into a folder
        'translations' inside the same location. It also assumes there is a 'babel.cfg' file and lazy_gettext
        is used next to general gettext methods.

        If you want to add a new language, add it to app.config['SUPPORTED_LANGUAGES'] and run this command.


Rate limiting
^^^^^^^^^^^^^

.. code-block:: python

    from pltk import limit

    @app.route('/rate-limited')
    @limit.rate(limit=300, per=60 * 15)
    def index():
        return '<h1>This is a rate limited response</h1>'


This would limit the function to be called 300 times per 15 minutes.

Before the function is executed it increments the rate limit with the help of the RateLimit class and stores an
instance of it on g as g._view_rate_limit. Also if the view is indeed over limit we automatically call a different
function instead.

The view function itself can get hold of the current rate limit by calling ::

    RateLimit.get_view_rate_limit().

We also give the key extra expiration_window seconds time to expire in redis so that badly synchronized clocks between
the workers and the redis server do not cause problems. Furthermore we use a pipeline (uses MULTI behind the scenes)
to make sure that we never increment a key without also setting the key expiration in case an exception happens between
those lines (for instance if the process is killed).


Setup locale
^^^^^^^^^^^^

.. code-block:: python

    from pltk import locale
    locale.setup_locale(babel, app):


Setup locale selector for given app. This will set up straitforward locale selector based on babel's request locale
best_match mechanizm.


Monitor command
^^^^^^^^^^^^^^^

.. code-block:: python

    from pltk import monitor_command
    monitor_command.main('tests.some.test', 'localhost', 'http', '8080', 'app'):


Script for running a regular nose test which uses the Werkzeug test client as a
monitoring command against any remote server.


Redis wrapper
^^^^^^^^^^^^^

.. code-block:: python

    from pltk import redis_wrapper
    redis = redis_wrapper.Redis(app)
    redis.set('some', 'value')

Module for Redis operations. Holds the Redis Flask wrapper. All you need is the app instance to create it.
It gets all setting from the application. You don't have to pass them manually.


Base test case
^^^^^^^^^^^^^^

.. code-block:: python

    from pltk import tests

    class MyTestCase(tests.TestCase):

        def test_something(self):
            response = self.get(self, '/foo', auth=False)
            self.assertTrue('test' in response.content)


Useful Flask base test case.


View
^^^^

.. code-block:: python

    from pltk import view

    def authorize(token):
        """We implement own authorize callback."""
        return token == 'ok'

    # then monkey patch it to the view module
    view.authorize = authorize


    class MyView(View):
        def get(self, query):
            """If request headers have json in ACCEPT. This result of a function will be encoded to json."""
            return {'result': [1, 2, 3]}


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on the
`GitHub project page <http://github.com/paylogic/pltk>`_.

License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `<LICENSE.txt>`_

© 2013 Paylogic International.
