#!/usr/bin/env python
"""
The Danabox command-line client issues API calls to the a Deis-Danabox controller.

Usage: danabox <command> [<args>...]

Auth commands::

  login         login to a Danabox with your Github ID
  logout        logout from Danabox

Subcommands, use ``danabox help [subcommand]`` to learn more::

  apps          manage applications used to provide services
  containers    manage containers used to handle requests and jobs
  config        manage environment variables that define app config
  builds        manage builds created using `danabox deploy`
  releases      manage releases of an application

  perms         manage permissions for shared apps and formations

Developer shortcut commands::

  create        create a new application
  deploy        deploy an application
  scale         scale containers by type (web=2, worker=1)
  info          view information about the current app
  open          open a URL to the app in a browser
  logs          view aggregated log info for the app
  run           run a command in an ephemeral app container
  destroy       destroy an application
"""


from __future__ import print_function
from cookielib import MozillaCookieJar
from getpass import getpass
from itertools import cycle
from threading import Event
from threading import Thread
import json
import os.path
import random
import socket
import subprocess
import sys
import time
import urlparse
import webbrowser
import yaml

from docopt import docopt
from docopt import DocoptExit
import requests

__version__ = '0.0.1'
DANABOX_API_URL = os.environ.get('DANABOX_API_URL') or 'http://danabox.io'


class Session(requests.Session):
    """
    Session for making API requests and interacting with the filesystem
    """

    def __init__(self):
        super(Session, self).__init__()
        self.trust_env = False
        cookie_file = os.path.expanduser('~/.danabox/cookies.txt')
        cookie_dir = os.path.dirname(cookie_file)
        self.cookies = MozillaCookieJar(cookie_file)
        # Create the $HOME/.danabox dir if it doesn't exist
        if not os.path.isdir(cookie_dir):
            os.mkdir(cookie_dir, 0700)
        # Load existing cookies if the cookies.txt exists
        if os.path.isfile(cookie_file):
            self.cookies.load()
            self.cookies.clear_expired_cookies()

    def clear(self):
        """Clear cookies"""
        try:
            self.cookies.clear()
            self.cookies.save()
        except KeyError:
            pass

    def git_root(self):
        """
        Return the absolute path from the git repository root

        If no git repository exists, raise an EnvironmentError
        """
        try:
            git_root = subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'],
                stderr=subprocess.PIPE).strip('\n')
        except subprocess.CalledProcessError:
            raise EnvironmentError('Current directory is not a git repository')
        return git_root

    def get_app(self):
        """
        Return the application name for the current directory

        The application is determined by parsing `git remote -v` output for the origin remote.

        Because Danabox only allows deployment of public Github repos we can create unique app
        names from a combination of the Github user's name and the repo name. Eg;
        'git@github.com:opdemand/example-ruby-sinatra.git' becomes 'opdemand-example--ruby--sinatra'

        If no application is found, raise an EnvironmentError.
        """
        git_root = self.git_root()
        remotes = subprocess.check_output(['git', 'remote', '-v'], cwd=git_root)
        if remotes is None:
            raise EnvironmentError('No git remotes found.')
        for remote in remotes.splitlines():
            if 'github.com' in remote:
                url = remote.split()[1]
                break
        if url is None:
            raise EnvironmentError('No Github remotes found.')
        pieces = url.split('/')
        owner = pieces[-2].split(':')[-1]
        repo = pieces[-1].replace('.git', '')
        app_raw = owner + '/' + repo
        app_name = app_raw.replace('-', '--').replace('/', '-')
        return app_name

    app = property(get_app)

    def request(self, *args, **kwargs):
        """
        Issue an HTTP request with proper cookie handling including
        `Django CSRF tokens <https://docs.djangoproject.com/en/dev/ref/contrib/csrf/>`
        """
        for cookie in self.cookies:
            if cookie.name == 'csrftoken':
                if 'headers' in kwargs:
                    kwargs['headers']['X-CSRFToken'] = cookie.value
                else:
                    kwargs['headers'] = {'X-CSRFToken': cookie.value}
                break
        response = super(Session, self).request(*args, **kwargs)
        self.cookies.save()
        return response


class Settings(dict):
    """
    Settings backed by a file in the user's home directory

    On init, settings are loaded from ~/.danabox/client.yaml
    """

    def __init__(self):
        path = os.path.expanduser('~/.danabox')
        if not os.path.exists(path):
            os.mkdir(path)
        self._path = os.path.join(path, 'client.yaml')
        if not os.path.exists(self._path):
            with open(self._path, 'w') as f:
                f.write(yaml.safe_dump({}))
        # load initial settings
        self.load()

    def load(self):
        """
        Deserialize and load settings from the filesystem
        """
        with open(self._path) as f:
            data = f.read()
        settings = yaml.safe_load(data)
        self.update(settings)
        return settings

    def save(self):
        """
        Serialize and save settings to the filesystem
        """
        data = yaml.safe_dump(dict(self))
        with open(self._path, 'w') as f:
            f.write(data)
        return data


_counter = 0


def _newname(template="Thread-{}"):
    """Generate a new thread name."""
    global _counter
    _counter += 1
    return template.format(_counter)


FRAMES = {
    'arrow':  ['^', '>', 'v', '<'],
    'dots': ['...', 'o..', '.o.', '..o'],
    'ligatures': ['bq', 'dp', 'qb', 'pd'],
    'lines': [' ', '-', '=', '#', '=', '-'],
    'slash':  ['-', '\\', '|', '/'],
}


class TextProgress(Thread):
    """Show progress for a long-running operation on the command-line."""

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        name = name or _newname("TextProgress-Thread-{}")
        style = kwargs.get('style', 'dots')
        super(TextProgress, self).__init__(
            group, target, name, args, kwargs)
        self.daemon = True
        self.cancelled = Event()
        self.frames = cycle(FRAMES[style])

    def run(self):
        """Write ASCII progress animation frames to stdout."""
        if not os.environ.get('DEIS_HIDE_PROGRESS'):
            time.sleep(0.5)
            self._write_frame(self.frames.next(), erase=False)
            while not self.cancelled.is_set():
                time.sleep(0.4)
                self._write_frame(self.frames.next())
            # clear the animation
            sys.stdout.write('\b' * (len(self.frames.next()) + 2))
            sys.stdout.flush()

    def cancel(self):
        """Set the animation thread as cancelled."""
        self.cancelled.set()

    def _write_frame(self, frame, erase=True):
        if erase:
            backspaces = '\b' * (len(frame) + 2)
        else:
            backspaces = ''
        sys.stdout.write("{} {} ".format(backspaces, frame))
        # flush stdout or we won't see the frame
        sys.stdout.flush()


def dictify(args):
    """Converts a list of key=val strings into a python dict.

    >>> dictify(['MONGODB_URL=http://mongolabs.com/test', 'scale=5'])
    {'MONGODB_URL': 'http://mongolabs.com/test', 'scale': 5}
    """
    data = {}
    for arg in args:
        try:
            var, val = arg.split('=')
        except ValueError:
            raise DocoptExit()
        # Try to coerce the value to an int since that's a common use case
        try:
            data[var] = int(val)
        except ValueError:
            data[var] = val
    return data


def trim(docstring):
    """
    Function to trim whitespace from docstring

    c/o PEP 257 Docstring Conventions
    <http://www.python.org/dev/peps/pep-0257/>
    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


def _rendevous(command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = urlparse.urlparse(DANABOX_API_URL).hostname
    s.connect((host, 6315))

    s.sendall("{}\n\r\n".format(command))

    while True:
        data = s.recv(1024)
        sys.stdout.write(data)
        if not data:
            break
    s.close()


class ResponseError(Exception):
    pass


class DanaboxClient(object):
    """
    A client which interacts with the Deis-Danabox controller.
    """

    def __init__(self):
        self._session = Session()
        self._settings = Settings()

    def _dispatch(self, method, path, body=None,
                  headers={'content-type': 'application/json'}, **kwargs):
        """
        Dispatch an API request to the active Deis-Danabox controller
        """
        func = getattr(self._session, method.lower())
        controller = DANABOX_API_URL
        url = urlparse.urljoin(controller, path, **kwargs)
        response = func(url, data=body, headers=headers)
        return response

    def apps(self, args):
        """
        Valid commands for apps:

        apps:create        create a new application
        apps:list          list accessible applications
        apps:info          view info about an application
        apps:deploy        deploy the app's code as committed to Github
        apps:open          open the application in a browser
        apps:logs          view aggregated application logs
        apps:run           run a command in an ephemeral app container
        apps:destroy       destroy an application

        Use `danabox help [command]` to learn more
        """
        return self.apps_list(args)

    def apps_calculate(self, args, quiet=False):
        """
        Calculate the application's JSON representation

        Usage: danabox apps:calculate [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        response = self._dispatch('post',
                                  "/api/apps/{}/calculate".format(app))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            databag = json.loads(response.content)
            if quiet is False:
                print(json.dumps(databag, indent=2))
            return databag
        else:
            raise ResponseError(response)

    def apps_create(self, args):
        """
        Create a new application

        Usage: danabox apps:create
        """
        try:
            self._session.git_root()  # check for a git repository
        except EnvironmentError:
            print('No git repository found, use `git init` to create one')
            sys.exit(1)
        data = {
            'id': self._session.get_app(),
            'formation': 'swanson'
        }
        sys.stdout.write('Creating application... ')
        sys.stdout.flush()
        try:
            progress = TextProgress()
            progress.start()
            response = self._dispatch('post', '/api/apps', json.dumps(data))
        finally:
            progress.cancel()
            progress.join()
        if response.status_code == requests.codes.created:  # @UndefinedVariable
            data = response.json()
            app_id = data['id']
            print("done, created {}".format(app_id))
        else:
            raise ResponseError(response)

    def apps_destroy(self, args):
        """
        Destroy an application

        Usage: danabox apps:destroy [--app=<id> --confirm=<confirm>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        confirm = args.get('--confirm')
        if confirm == app:
            pass
        else:
            print("""
 !    WARNING: Potentially Destructive Action
 !    This command will destroy the application: {app}
 !    To proceed, type "{app}" or re-run this command with --confirm={app}
""".format(**locals()))
            confirm = raw_input('> ').strip('\n')
            if confirm != app:
                print('Destroy aborted')
                return
        sys.stdout.write("Destroying {}... ".format(app))
        sys.stdout.flush()
        try:
            progress = TextProgress()
            progress.start()
            before = time.time()
            response = self._dispatch('delete', "/api/apps/{}".format(app))
        finally:
            progress.cancel()
            progress.join()
        if response.status_code in (requests.codes.no_content,  # @UndefinedVariable
                                    requests.codes.not_found):  # @UndefinedVariable
            print('done in {}s'.format(int(time.time() - before)))
        else:
            raise ResponseError(response)

    def apps_list(self, args):
        """
        List applications visible to the current user

        Usage: danabox apps:list
        """
        response = self._dispatch('get', '/api/apps')
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            data = response.json()
            print('=== Apps')
            for item in data['results']:
                print('{id} {containers}'.format(**item))
        else:
            raise ResponseError(response)

    def apps_info(self, args):
        """
        Print info about the current application

        Usage: danabox apps:info [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        response = self._dispatch('get', "/api/apps/{}".format(app))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            print("=== {} Application".format(app))
            print(json.dumps(response.json(), indent=2))
            print()
            self.containers_list(args)
            print()
        else:
            raise ResponseError(response)

    def apps_deploy(self, args):
        """
        Deploy the app's code as currently committed to Github.

        Even though this command requires that you are inside a git repo to determine which app
        to deploy, the actual deployment is done on the Controller.

        Usage: danabox apps:deploy  [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        url = "{}/api/apps/{}/deploy".format(DANABOX_API_URL, app)
        secret = self._session.get(url, stream=True).content.replace('"', '')
        if "Not found" in secret:
            raise ResponseError("App doesn't exist. Perhaps you need to do `danabox create` first?")
        cmd = "BUILD\n{}".format(secret)
        _rendevous(cmd)

    def apps_open(self, args):
        """
        Open a URL to the application in a browser

        Usage: danabox apps:open [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        # TODO: replace with a proxy lookup that doesn't have any side effects
        # this currently recalculates and updates the databag
        response = self._dispatch('post',
                                  "/api/apps/{}/calculate".format(app))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            databag = json.loads(response.content)
            domains = databag.get('domains', [])
            if domains:
                domain = random.choice(domains)
                # use the OS's default handler to open this URL
                webbrowser.open('http://{}/'.format(domain))
                return domain
            else:
                print('No proxies found. Use `deis nodes:scale myformation proxy=1` to scale up.')
        else:
            raise ResponseError(response)

    def apps_logs(self, args):
        """
        Retrieve the most recent log events

        Usage: danabox apps:logs [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        response = self._dispatch('post',
                                  "/api/apps/{}/logs".format(app))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            print(response.json())
        else:
            raise ResponseError(response)

    def apps_run(self, args):
        """
        Run a command inside an ephemeral app container

        Usage: danabox apps:run <command>...
        """
        app = self._session.app
        body = {'command': ' '.join(sys.argv[2:])}
        response = self._dispatch('post',
                                  "/api/apps/{}/run".format(app),
                                  json.dumps(body))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            output, rc = json.loads(response.content)
            if rc != 0:
                print('Warning: non-zero return code {}'.format(rc))
            sys.stdout.write(output)
            sys.stdout.flush()
        else:
            raise ResponseError(response)

    def auth_login(self, args):
        """
        Login by authenticating against the Deis-Danabox Controller

        Usage: danabox auth:login [options]

        Options:

        --username=USERNAME    Github username
        --password=PASSWORD    Github password
        --oauth-key=OAUTH_KEY  OAuth key obtained from web flow
        """
        print("""Danabox uses your Github identity to authenticate. Danabox does not store your Github password.""")
        oauth_key = args.get('--oauth-key')
        if oauth_key:
            # TODO: not implemeted on the API yet.
            payload = {'oauth_key': oauth_key}
        else:
            username = args.get('--username')
            if not username:
                username = raw_input('Github username: ')
            password = args.get('--password')
            if not password:
                password = getpass('Github password: ')
            payload = {'username': username, 'password': password}
        url = urlparse.urljoin(DANABOX_API_URL, '/api/auth/github')
        response = self._session.post(url, data=payload, allow_redirects=False)
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            oauth_token = response.content.replace('"', '')
            if self._login(username, oauth_token):
                self._settings['username'] = username
                self._settings.save()
                print('Logged in as {}'.format(username))
            else:
                print('Login failed')
            return
        else:
            print('Github authentication failed', response.content)
            return False

    def auth_show_token(self, args):
        """
        Just a convenience method to show your current Github token. Handy if you want to login
        with the deis client instead because it uses the token as the password.

        Usage: danabox auth:show_token [options]

        Options:

        --username=USERNAME    Github username
        --password=PASSWORD    Github password
        """
        username = args.get('--username')
        if not username:
            username = raw_input('Github username: ')
        password = args.get('--password')
        if not password:
            password = getpass('Github password: ')
        payload = {'username': username, 'password': password}
        url = urlparse.urljoin(DANABOX_API_URL, '/api/auth/github')
        token = self._session.post(url, data=payload, allow_redirects=False).content
        print("Your current Github token is: %s" % token)

    def auth_cancel(self, args):
        """
        Cancel and remove the current account.

        Usage: danabox auth:cancel
        """
        print('Please log in again in order to cancel this account')
        username = self.auth_login()
        if username:
            confirm = raw_input("Cancel account \"{}\"? (y/n) ".format(username))
            if confirm == 'y':
                self._dispatch('delete', '/api/auth/cancel')
                self._session.cookies.clear()
                self._session.cookies.save()
                self._settings['controller'] = None
                self._settings.save()
                print('Account cancelled')
            else:
                print('Accont not changed')

    def _login(self, username, oauth_token):
        """
        Login using Django's native session authentication.
        The password field is always the Github OAuth token.
        """
        headers = {}
        payload = {'username': username, 'password': oauth_token}
        url = urlparse.urljoin(DANABOX_API_URL, '/api/auth/login/')
        # clear any cookies for the domain
        self._session.cookies.clear()
        # prime cookies for login
        self._session.get(url, headers=headers)
        # post credentials to the login URL
        response = self._session.post(url, data=payload, allow_redirects=False)
        if response.status_code == requests.codes.found:  # @UndefinedVariable
            return username
        else:
            self._session.cookies.clear()
            self._session.cookies.save()
            return False

    def auth_logout(self, args):
        """
        Logout from the Deis-Danabox Controller and clear the user session

        Usage: danabox auth:logout
        """
        self._dispatch('get', '/api/auth/logout/')
        self._session.cookies.clear()
        self._session.cookies.save()
        print('Logged out')

    def builds(self, args):
        """
        Valid commands for builds:

        builds:list        list build history for a formation
        builds:create      coming soon!

        Use `danabox help [command]` to learn more
        """
        return self.builds_list(args)

    def builds_list(self, args):
        """
        List build history for a formation

        Usage: danabox builds:list [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        response = self._dispatch('get', "/api/apps/{}/builds".format(app))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            print("=== {} Builds".format(app))
            data = response.json()
            for item in data['results']:
                print("{0[uuid]:<23} {0[created]}".format(item))
        else:
            raise ResponseError(response)

    def config(self, args):
        """
        Valid commands for config:

        config:list        list environment variables for an app
        config:set         set environment variables for an app
        config:unset       unset environment variables for an app

        Use `danabox help [command]` to learn more
        """
        return self.config_list(args)

    def config_list(self, args):
        """
        List environment variables for an application

        Usage: danabox config:list [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        response = self._dispatch('get', "/api/apps/{}/config".format(app))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            config = response.json()
            values = json.loads(config['values'])
            print("=== {} Config".format(app))
            items = values.items()
            if len(items) == 0:
                print('No configuration')
                return
            for k, v in values.items():
                print("{k}: {v}".format(**locals()))
        else:
            raise ResponseError(response)

    def config_set(self, args):
        """
        Set environment variables for an application

        Usage: danabox config:set <var>=<value>... [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        body = {'values': json.dumps(dictify(args['<var>=<value>']))}
        response = self._dispatch('post',
                                  "/api/apps/{}/config".format(app),
                                  json.dumps(body))
        if response.status_code == requests.codes.created:  # @UndefinedVariable
            config = response.json()
            values = json.loads(config['values'])
            print("=== {}".format(app))
            items = values.items()
            if len(items) == 0:
                print('No configuration')
                return
            for k, v in values.items():
                print("{k}: {v}".format(**locals()))
        else:
            raise ResponseError(response)

    def config_unset(self, args):
        """
        Unset an environment variable for an application

        Usage: danabox config:unset <key>... [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        values = {}
        for k in args.get('<key>'):
            values[k] = None
        body = {'values': json.dumps(values)}
        response = self._dispatch('post',
                                  "/api/apps/{}/config".format(app),
                                  json.dumps(body))
        if response.status_code == requests.codes.created:  # @UndefinedVariable
            config = response.json()
            values = json.loads(config['values'])
            print("=== {}".format(app))
            items = values.items()
            if len(items) == 0:
                print('No configuration')
                return
            for k, v in values.items():
                print("{k}: {v}".format(**locals()))
        else:
            raise ResponseError(response)

    def containers(self, args):
        """
        Valid commands for containers:

        containers:list        list application containers
        containers:scale       scale app containers (e.g. web=4 worker=2)

        Use `danabox help [command]` to learn more
        """
        return self.containers_list(args)

    def containers_list(self, args):
        """
        List containers servicing an application

        Usage: danabox containers:list [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.get_app()
        response = self._dispatch('get',
                                  "/api/apps/{}/containers".format(app))
        if response.status_code != requests.codes.ok:  # @UndefinedVariable
            raise ResponseError(response)
        containers = response.json()
        response = self._dispatch('get', "/api/apps/{}/builds".format(app))
        if response.status_code != requests.codes.ok:  # @UndefinedVariable
            raise ResponseError(response)
        txt = response.json()['results'][0]['procfile']
        procfile = json.loads(txt) if txt else {}
        print("=== {} Containers".format(app))
        c_map = {}
        for item in containers['results']:
            c_map.setdefault(item['type'], []).append(item)
        print()
        for c_type in c_map.keys():
            command = procfile.get(c_type, '<none>')
            print("--- {c_type}: `{command}`".format(**locals()))
            for c in c_map[c_type]:
                print("{type}.{num} up {created} ({node})".format(**c))
            print()

    def containers_scale(self, args):
        """
        Scale an application's containers by type

        Example: danabox containers:scale web=4 worker=2

        Usage: danabox containers:scale <type=num>... [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.get_app()
        body = {}
        for type_num in args.get('<type=num>'):
            typ, count = type_num.split('=')
            body.update({typ: int(count)})
        print('Scaling containers... but first, coffee!')
        try:
            progress = TextProgress()
            progress.start()
            before = time.time()
            response = self._dispatch('post',
                                      "/api/apps/{}/scale".format(app),
                                      json.dumps(body))
        finally:
            progress.cancel()
            progress.join()
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            print('done in {}s\n'.format(int(time.time() - before)))
            self.containers_list({})
        else:
            raise ResponseError(response)

    def perms(self, args):
        """
        Valid commands for perms:

        perms:list            list permissions granted on an app or formation
        perms:create          create a new permission for a user
        perms:delete          delete a permission for a user

        Use `deis help perms:[command]` to learn more
        """
        # perms:transfer        transfer ownership of an app or formation
        return self.perms_list(args)

    def perms_list(self, args):
        """
        List all users with permission to use an app, or list all users
        with system administrator privileges.

        Usage: deis perms:list [--app=<app>|--admin]
        """
        app, url = self._parse_perms_args(args)
        response = self._dispatch('get', url)
        if response.status_code == requests.codes.ok:
            print(json.dumps(response.json(), indent=2))
        else:
            raise ResponseError(response)

    def perms_create(self, args):
        """
        Give another user permission to use an app, or give another user
        system administrator privileges.

        Usage: deis perms:create <username> [--app=<app>|--admin]
        """
        app, url = self._parse_perms_args(args)
        username = args.get('<username>')
        body = {'username': username}
        if app:
            msg = "Adding {} to {} collaborators... ".format(username, app)
        else:
            msg = "Adding {} to system administrators... ".format(username)
        sys.stdout.write(msg)
        sys.stdout.flush()
        response = self._dispatch('post', url, json.dumps(body))
        if response.status_code == requests.codes.created:
            print('done')
        else:
            raise ResponseError(response)

    def perms_delete(self, args):
        """
        Revoke another user's permission to use an app, or revoke another
        user's system administrator privileges.

        Usage: deis perms:delete <username> [--app=<app>|--admin]
        """
        app, url = self._parse_perms_args(args)
        username = args.get('<username>')
        url = "{}/{}".format(url, username)
        if app:
            msg = "Removing {} from {} collaborators... ".format(username, app)
        else:
            msg = "Remove {} from system administrators... ".format(username)
        sys.stdout.write(msg)
        sys.stdout.flush()
        response = self._dispatch('delete', url)
        if response.status_code == requests.codes.no_content:
            print('done')
        else:
            raise ResponseError(response)

    def _parse_perms_args(self, args):
        app = args.get('--app'),
        admin = args.get('--admin')
        if admin:
            app = None
            url = '/api/admin/perms'
        else:
            app = app[0] or self._session.app
            url = "/api/apps/{}/perms".format(app)
        return app, url

    def releases(self, args):
        """
        Valid commands for releases:

        releases:list        list an application's release history
        releases:info        print information about a specific release
        releases:rollback    coming soon!

        Use `danabox help [command]` to learn more
        """
        return self.releases_list(args)

    def releases_info(self, args):
        """
        Print info about a particular release

        Usage: danabox releases:info <version> [--app=<app>]
        """
        version = args.get('<version>')
        app = args.get('--app')
        if not app:
            app = self._session.app
        response = self._dispatch(
            'get', "/api/apps/{app}/releases/{version}".format(**locals()))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            print(json.dumps(response.json(), indent=2))
        else:
            raise ResponseError(response)

    def releases_list(self, args):
        """
        List release history for an application

        Usage: danabox releases:list [--app=<app>]
        """
        app = args.get('--app')
        if not app:
            app = self._session.app
        response = self._dispatch('get', '/api/apps/{app}/releases'.format(**locals()))
        if response.status_code == requests.codes.ok:  # @UndefinedVariable
            print('=== {0} Releases'.format(app))
            data = response.json()
            for item in data['results']:
                print('{version} {created}'.format(**item))
        else:
            raise ResponseError(response)


def parse_args(cmd):
    """
    Parse command-line args applying shortcuts and looking for help flags
    """
    shortcuts = {
        'login': 'auth:login',
        'logout': 'auth:logout',
        'create': 'apps:create',
        'deploy': 'apps:deploy',
        'destroy': 'apps:destroy',
        'ps': 'containers:list',
        'info': 'apps:info',
        'scale': 'containers:scale',
        'calculate': 'apps:calculate',
        'open': 'apps:open',
        'logs': 'apps:logs',
        'run': 'apps:run',
    }
    if cmd == 'help':
        cmd = sys.argv[-1]
        help_flag = True
    else:
        cmd = sys.argv[1]
        help_flag = False
    # swap cmd with shortcut
    if cmd in shortcuts:
        cmd = shortcuts[cmd]
        # change the cmdline arg itself for docopt
        if not help_flag:
            sys.argv[1] = cmd
        else:
            sys.argv[2] = cmd
    # convert : to _ for matching method names and docstrings
    if ':' in cmd:
        cmd = '_'.join(cmd.split(':'))
    return cmd, help_flag


def main():
    """
    Create a client, parse the arguments received on the command line, and
    call the appropriate method on the client.
    """
    cli = DanaboxClient()
    args = docopt(__doc__, version='Danabox CLI {}'.format(__version__),
                  options_first=True)
    cmd = args['<command>']
    cmd, help_flag = parse_args(cmd)
    # print help if it was asked for
    if help_flag:
        if cmd != 'help':
            if cmd in dir(cli):
                print(trim(getattr(cli, cmd).__doc__))
                return
        docopt(__doc__, argv=['--help'])
    # unless cmd needs to use sys.argv directly
    if hasattr(cli, cmd):
        method = getattr(cli, cmd)
    else:
        raise DocoptExit('Found no matching command, try `danabox help`')
    # re-parse docopt with the relevant docstring unless it needs sys.argv
    if cmd not in ('apps_run',):
        docstring = trim(getattr(cli, cmd).__doc__)
        if 'Usage: ' in docstring:
            args.update(docopt(docstring))
    # dispatch the CLI command
    try:
        method(args)
    except EnvironmentError as err:
        raise DocoptExit(err.message)
    except ResponseError as err:
        resp = err.message
        print('{} {}'.format(resp.status_code, resp.reason))
        try:
            msg = resp.json()
        except:
            msg = resp.text
        print(msg)
        sys.exit(1)


if __name__ == '__main__':
    main()
    sys.exit(0)
