""" Flask Management Commands."""
from flask import url_for
from subprocess import call
import cmd
import os.path as op
import os
import sys
import json
from socket import gethostname
from datetime import date
from pltk.flask_utils.monitor_command import main as monitor_command_main


# Declare options only if they are different from --option=value
DBCOMMANDS = {
    'mysql': ['mysql', {'username': '--user={0}', 'database': '{0}'}],
    'postgresql': ['psql', {'database': '{0}', 'password': None}],
    'sqlite': ['sqlite3', {'database': '{0}'}],
    # Special case NoSQL
    'mongo': ['mongo', None]}


def install_commands(app, manager, db, model_collector):
    """
    Installs the management commands.
    """

    @manager.command
    def monitor_test(Test_name=None,
                     Host='127.0.0.1',
                     Scheme='http',
                     Port='5000',
                     R_prefix=''):
        """
        Run a test as monitor command.
                Example usage:
                #> app monitor_test \\
                   -T app.tests.test_utils:TestView \\
                   -H dev.app.com -P 443 -R /unstable -S https
        """
        monitor_command_main(Test_name, Host, Scheme, Port, R_prefix)

    @manager.command
    def shell():
        """Run Python shell with application context."""
        ctx = {'app': app,
               'db': db,
               'url_for': url_for,
               }

        for bp in ctx['app'].blueprints.values():
            for name, document in model_collector(bp.import_name):
                if name not in ctx:
                    ctx[name] = document

            try:
                from IPython import embed
                embed(user_ns=ctx)
            except ImportError:
                try:
                    from IPython.Shell import IPShellEmbed
                    IPShellEmbed()(global_ns=ctx)
                except ImportError:
                    import code
                    code.interact(local=ctx)

    @manager.command
    def dbshell():
        """Run database shell."""
        args = []
        try:
            cmd, conf = DBCOMMANDS[db.engine.name]
            args.append(cmd)
        except AttributeError:
            mongo_database = app.config.get('MONGODB_DB')
            # mongodb is an exception, so if there's config setting then we use it as angine
            if mongo_database:
                cmd = DBCOMMANDS['mongo'][0]
                args.append(cmd)
                args.append(mongo_database)

        for arg in ['username', 'password', 'host', 'port', 'database']:
            try:
                value = getattr(db.engine.url, arg)
                if value:
                    src = conf.get(arg, '--{0}={{0}}'.format(arg))  # --option=value
                    if src:
                        args.append(src.format(value))
            except AttributeError:
                pass

        try:
            return call(args)
        except OSError as e:
            if e.errno == 2:
                print('Executable for your database not found: {0}'.format(cmd))
                return 1
            raise

    @manager.command
    def http():
        """Run HTTP emulating console.
        Examples:
            - POST /foo/bar list=[1,2,3,4]
            - POST /user/login email=a@b.com password=p
            - GET /user/profile
            - header Authorization 1232123123
        """
        console = HttpConsole(app)
        console.prompt = '> '
        import readline
        try:
            readline.read_history_file(console.history_file)
        except IOError:
            pass
        try:
            console.cmdloop()
        except KeyboardInterrupt:
            pass
        finally:
            console.save_history()

    @manager.command
    def print_settings():
        """Print all current Flask Settings."""
        print(app.config)

    @manager.command
    def ec2_backup(access_key,
                   secret_key,
                   user_id,
                   Pem_file='/mnt/pk.pem',
                   cert_file='/mnt/cert.pem',
                   platform='i386',
                   bucket='backups.{0}'.format(gethostname()),
                   ec2_path='/usr/bin/'
                   ):
        """
        Create an ami from the current server and pushes its contents to s3. Will
        only print(the commands if app.debug == True, thus not executing
        anything.
        """
        # weekday() is localized and might start with 0 or 1 so we add sunday twice
        days = (
            'sunday', 'monday',
            'tuesday', 'wednesday',
            'thursday', 'friday',
            'saturday', 'sunday')
        manifest = days[date.today().weekday()]

        step_1 = 'rm -f /mnt/{0}*'.format(manifest)
        step_2 = '{0}ec2-bundle-vol -p {1} -d /mnt -k {2} -c {3} -u {4} -r {5}'.format(
            ec2_path, manifest, Pem_file, cert_file, user_id, platform)
        step_3 = '{0}ec2-upload-bundle -b {1} -m /mnt/{2}.manifest.xml -a {3} -s {4}'.format(
            ec2_path, bucket, manifest, access_key, secret_key)

        if app.debug:
            print('DEBUG:', step_1)
            print('DEBUG:', step_2)
            print('DEBUG:', step_3)
            return

        os.system(step_1)
        os.system(step_2)
        os.system(step_3)

    @manager.command
    def compile_messages():
        """Update the gettext messages.pot file and initialize the supported languages (if not already) and compile
        the messages to .mo files."""
        working_dir = os.path.abspath(app.root_path)
        translations_dir = os.path.join(working_dir, 'translations')

        if not os.path.exists(translations_dir):
            os.mkdir(translations_dir)

        os.system(
            'pybabel extract -F {0}/babel.cfg -k lazy_gettext -o {1}/messages.pot {2}'.format(
                working_dir, working_dir, working_dir))

        for language in app.config['SUPPORTED_LANGUAGES']:
            if language != 'en':
                if not os.path.exists(os.path.join(translations_dir, language)):
                    os.system(
                        'pybabel init -i {0}/messages.pot -d {1} -l {2}'.format(
                            working_dir, translations_dir, language))
        os.system('pybabel update -i {0}/messages.pot -d {1}'.format(
            working_dir, translations_dir))
        os.system('pybabel compile -d {0}'.format(translations_dir))


class HttpConsole(cmd.Cmd):
    """Http-based CLI interface."""

    history_file = op.expanduser('~/.pltk-history')

    def __init__(self, app, version='0.1'):
        cmd.Cmd.__init__(self)
        self.client = app.test_client()
        self.version = version
        self.headers = []

    def save_history(self):
        """Save history to the history file."""
        import readline
        readline.write_history_file(self.history_file)

    def request(self, method, url, data=None):
        """Issue a request."""
        url = '/{0}{1}'.format(self.version, url)
        try:
            res = getattr(self.client, method)(url, data=data, content_type='application/json',
                                               headers=self.headers)
        except Exception:
            import traceback
            traceback.print_exc(file=sys.stderr)
            return
        print('{0} {1} {2}'.format(method.upper(), url, res.status))
        for h in res.headers:
            print('{0}: {1}'.format(h))
        if res.data:
            print(res.data)

    def do_exit(self, line):
        """Exit."""
        sys.exit()
    do_EOF = do_exit

    def do_get(self, line):
        """Issue a GET request."""
        self.request('get', line)
    do_GET = do_get

    def do_post(self, line):
        """Issue a POST request."""
        data = line.split()
        url = data[0]
        data = data[1:]
        self.request('post', url, jsonize(data))
    do_POST = do_post

    def do_header(self, line):
        """Set up the headers."""
        if not line:
            for h in self.headers:
                print('{0}: {1}'.format(h))
            return
        header = line.split(' ', 1)
        if len(header) == 2:
            self.headers.append(tuple(header))
        else:
            for i, (k, _) in enumerate(self.headers):
                if k == header[0]:
                    del self.headers[i]
                    break


def jsonize(data):
    """Convert data to a json string.

    Data is a string that describes value assignment to
    variables. Values are strings (without spaces) or lists, where
    items are separated with a comma.

    For example, `'a=[1,two,three]'` will return `'{"a": ["1", "two", "three"]}'`.

    """
    if isinstance(data, str):
        data = data.split()
    values = {}
    for pair in data:
        # In case that a list is receive remove the [] and jsonize it correctly
        try:
            key, value = pair.split('=')
        except ValueError:
            key, value = pair, ''
            print(('\nWARNING: The spaces are allowed only to separate '
                   'commands, if you are sending a list must be separated by '
                   'comma without spaces.\n'))
            return
        if value.startswith('[') and value.endswith(']'):
            value = [x for x in value[1:-1].split(',')]
        values.update({key: value})
    return json.dumps(values)
