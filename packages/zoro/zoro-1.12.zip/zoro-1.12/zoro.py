"""
Zoro
====

This is a helper module for creating zorofiles.


Copyright (c)2014 by Branko Vukelic <branko@brankovukelic.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

from __future__ import unicode_literals, print_function

import re
import shlex
import subprocess
import platform
import os
import time
import sys
import shutil
import fnmatch
import stat
import optparse
import datetime

from shutil import (copy, copy2, copytree, rmtree, move)
from os import (remove, removedirs, rename, renames, rmdir)

try:
    from watchdog.events import PatternMatchingEventHandler
    from watchdog.observers import Observer
    from watchdog.observers.read_directory_changes import WindowsApiObserver
    nowatch = False
except ImportError:
    # watchdog is not installed
    nowatch = True


__author__ = 'Branko Vukelic'
__version__ = '1.12'


class NoTargetError(Exception):
    pass


if nowatch is False:
    class PatternWatcher(PatternMatchingEventHandler):
        """ Event handler used for monitoring file changes with watchdog

        This is a subclass of ``watchdog.events.PatternMatchingEventHandler``,
        so it is suitable for watching glob patterns within a subtree of a
        project. It is not meant to be used directly, but through a wrapper
        function ``watch()``.

        Please do not rely on this class' API since it's considered an internal
        implementation detail and not offered as an API.

        """

        def __init__(self, fn, *args, **kwargs):
            self.fn = fn
            super(PatternWatcher, self).__init__(*args, **kwargs)

        def run(self, reason='some unknown fs event'):
            print('Restarting at %s because of %s' % (datetime.datetime.now(),
                                                      reason))
            self.fn()

        def on_modified(self, event):
            self.run('file/directory modification')

# You can use this to print separators
separator = '\n\n-------------------------------------------------------\n\n'


def environ(name):
    """ Read environment variable

    This is a shortcut for ``os.environ.get()`` call.

    """

    return os.environ.get(name)


def setenv(name, value):
    """ Sets the environment variable """
    os.environ[name] = value


def venv():
    """ Gets the name of the virtualenv we are in

    This function will return the value of the ``VIRTUAL_ENV`` environment
    variable, which should correspond to the name of the active virtualenv (if
    any).

    """

    return environ('VIRTUAL_ENV')


def get_filename(path):
    """ Returns filename without extension

    This function extracts the filename without extension from a full path.

    """

    return os.path.splitext(os.path.basename(path))[0]


def where(cmd):
    """ Looks up the PATH and finds executables returning None if not found

    This is a Python version of commands like ``where`` and ``which``. It will
    look for executables on the system ``PATH`` and return the full path for
    the command. On platforms like Windows, you do not need to specify any of
    the common executable extensions since the function will try '.exe',
    '.cmd', and '.bat' automatically.

    The intention is to make this function completely platform independent so
    this function should be used in preference over native shell commands.

    This function is a modified version of a `StackOverflow answer`_, which
    takes into account the common aliases for commands on Windows OS.

    .. _StackOverflow answer: http://stackoverflow.com/a/377028/234932

    """

    def is_exe(path):
        return os.path.isfile(path) and os.access(path, os.X_OK)

    filename = os.path.basename(cmd)
    filedir = os.path.dirname(cmd)

    if filedir:
        if is_exe(cmd):
            return cmd
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            executable = os.path.join(path, cmd)
            if is_exe(executable):
                return executable

    if platform.system() != 'Windows':
        return None

    if cmd.endswith('.exe'):
        return where('%s.cmd' % get_filename(cmd))

    if cmd.endswith('.cmd'):
        return where('%s.bat' % get_filename(cmd))

    if cmd.endswith('.bat'):
        return None

    return where('%s.exe' % get_filename(cmd))


def yesno(prompt, default='y'):
    """ Asks a yes/no question and return the answer as boolean

    Prompts the user for a choce between Yes and No ('y' and 'n'). The return
    value is a boolean value that tells us whether user answered 'y'.

    Choices are resitricted to 'y' and 'n', and the function will not allow any
    other values.

    The ``default`` argument can be used to specify a letter that should be the
    default (default is 'y'). Depending on the this argument the prompt will be
    suffixed with either '[Y/n]' or '[y/N]' where the upper-case letter is
    supposed to represent the default.

    Example::

        >>> yesno('Can you see this?', default='n')
        Can you see this? [y/N]: _

    """

    if default == 'y':
        choices = '[Y/n]'
    else:
        choices = '[y/N]'

    def get_choice():
        s = raw_input('%s %s: ' % (prompt, choices))
        if s:
            return s[0].lower()
        return default

    choice = get_choice()

    while choice and choice not in ['y', 'n']:
        print("Please type 'y' or 'n'")
        choice = get_choice()

    choice = choice or default

    return choice == 'y'


def ask(prompt, default=None):
    """ Obtains user input with optional default if there is no input

    Prompts the user for input and returns the entered value. If the default
    value is supplied (and is not None), the prompt will be suffixed with
    '[DEFAULT]' where 'DEFAULT' is the value of the ``default`` argument.

    Example::

        >>> ask('What is your name?', default='Anonymous')
        What is your name? [Anonymous]: _

    """

    if default is not None:
        prompt += ' [%s]' % default
    return raw_input('%s: ' % prompt) or default


def err(msg, exit=False):
    """ Writes message to ``stderr`` and exits if exit is not False

    The main function of this script is to write to ``stderr``.

    The second argument represent the status code that should be returned on
    exit. When this is set to ``False`` the function will no cause the script
    to terminate (which is the default), but only write to stderr.

    Example::

        >>> err('Oops!', 1)

    """

    sys.stderr.write(msg)
    if exit is not False:
        sys.exit(exit)


def write(path, content):
    """ Writes content to a file at path

    This function is a user-friendly way to write to files. It will prompt the
    user before writing to existing files, and it will do basic housekeeping by
    closing the file after writing.

    Its writes are not encoded, so you should make sure the content is properly
    encoded before writing. You should also note that it will write using the
    ``w`` flag, so any contents in existing files will be overwritten.

        >>> write('example.txt', 'This is just an example')
        >>> write('existing.txt', 'I killed your filez, muwahaha!')
        existing.txt exists. Overwrite? [y/N]: _

    """

    if os.path.exists(path) and not yesno('%s exists. Overwrite?' % path, 'n'):
        return
    f = open(path, 'w')
    f.write(content)
    f.close()


def read(path):
    """ Reads a file

    Reads from a file and returns its unprocessed contents. If the file does
    not exist, ``None`` is returned instead.

        >>> read('example.txt')
        'This is just an example'

    """

    if not os.path.exists(path):
        return
    f = open(path, 'r')
    content = f.read()
    f.close()
    return content


def install_requirements(path, wait=True):
    """ Install from requirements file using pip """
    return run('pip install -r %s' % path, wait=wait)


def pip_install(package_name, wait=True):
    """ Install a package using pip """
    return run('pip install %s' % package_name, wait=wait)


def easy_install(package_name, wait=True):
    """ Install a package using easy_install """
    return run('easy_install %s' % package_name, wait=wait)


def install_node_requirements(wait=True):
    """ Install requirements from package.json using NPM """
    return run('npm install', wait=wait)


def npm_install(package_name, wait=True):
    """ Install a package using NPM """
    return run('npm install %s' % package_name, wait=wait)


def patch(path, patch_fn):
    """ Patches a file using the patch_fn

    This function will open the specified path, read it contents, pass it to
    ``patch_fn``, and write back the function's return value to the same file.

    Example::

        >>> patch('example.txt', lambda s: s.upper())
        >>> read('example.txt')
        'THIS IS JUST AN EXAMPLE'

    """

    if not os.path.exists(path):
        return
    f = open(path, 'r')
    content = f.read()
    f.close()
    f = open(path, 'w')
    f.write(patch_fn(content))
    f.close()


def cleanup(path, pattern):
    """ Remove all files and directories under ``path`` that match ``pattern``

    This function takes a root path, and a glob pattern, and removes any files
    or directories that match the pattern recursively.

    Example::

        >>> cleanup('src', '*.pyc')

    """

    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, pattern):
            remove(os.path.join(root, filename))
        for dirname in fnmatch.filter(dirs, pattern):
            rmtree(os.path.join(root, dirname))


def cmdargs(cmd):
    """ Splits the command into list using shlex, and leaves lists intact

    This function is a wrapper around ``shlex.split()`` which splits strings
    and leaves iterables alone.

    It is used internally throughout the ``zoro`` module to allow specifying of
    commands as both strings, and lists and tuples.

    Example::

        >>> cmdargs('foo bar baz')
        ['foo', 'bar', 'baz']
        >>> cmdargs(['bar', 'foo'])
        ['bar', 'foo']

    """

    if not hasattr(cmd, '__iter__'):
        return shlex.split(cmd)
    return cmd


def node_local(cmd):
    """ Returns command for locally instaled NodeJS command-line scripts

    Builds a local ``node_modules/.bin`` version of the command. This is done
    to ease calling NodeJS scripts that are installed inside the project
    directory as dependencies.

    This function only returns the command as a list. It doesn't check if the
    command actually exists, nor does it run it. Use it with ``run()`` or
    ``watch()``.

    Note that any arguments that you supply are preserved.

    Example::

        >>> node_local('r.js')
        ['node', 'node_modules/.bin/r.js']

        >>> node_local('r.js -o build.js')
        ['node', 'node_modules/.bin/r.js', '-o', 'build.js']

    On Windows::

        >>> node_local('r.js')
        ['node_modules/.bin/r.js.cmd']

        >>> node_local('r.js -o build.js')
        ['node_modules/.bin/r.js.cmd', '-o', 'build.js']

    """

    cmd = cmdargs(cmd)
    cmd[0] = os.path.normpath('node_modules/.bin/%s' % cmd[0])
    if platform.system() == 'Windows':
        cmd[0] += '.cmd'
    else:
        cmd.insert(0, 'node')
    return cmd


def python(cmd):
    """ Returns command for python scripts

    This is a simple utility function that adds a ``.py`` extension to
    specified command and prefixes it with ``python``.

    The function only returns the command as a list. It doesn't check whether
    the script exists or whether it needs a ``.py`` extension, nor does it run
    the command. Use it with ``run()`` and ``watch()``.

    Example::

        >>> python('toutf sometext.txt')
        ['python', 'toutf.py', 'sometext.txt']

    """

    cmd = cmdargs(cmd)
    cmd[0] = '%s.py' % os.path.normpath(cmd[0])
    cmd.insert(0, 'python')
    return cmd


def run(cmd, wait=False, env={}):
    """ Runs a command

    Runs a command either asynchronously (default) or synchronusly with
    optional environment specific to the subprocess.

    The ``cmd`` argument can either be a string or a list.

    Note that the default behavior is non-blocking (the function will not block
    and wait for the command to exit). If you want the function to block until
    the command is finished, pass ``True`` as ``wait`` argument.

    If you want the command to run with environment variables that you do not
    want to set globally, run it with ``env`` argument. The argument should be
    a dict of variable-value pairs.

    Return value of the function is a handle for the child process. This is a
    return value of ``subprocess.Popen()``, so look at the Python documentation
    for more details on how to use this value.

    Any commands you run will share the STDOUT and STDIN with the parent
    process. Because of this, running multiple commands in parallel
    (asynchronously, without the ``wait`` flag) will cause their output to be
    mixed in the terminal in which the calling script was run. This is
    intentional.

    Example::

        >>> run('compass watch')  # run will not wait for watch to end
        >>> run('compass compile', wait=True)  # run waits for compile to end
        >>> run(python('myapp'), env={'APP_ENV': 'DEVELOPMENT'})

    """

    cmd = cmdargs(cmd)
    env = os.environ.copy().update(env)
    child = subprocess.Popen(cmd, shell=True, env=env)
    if wait:
        child.wait()
    return child


def watch(cmd, watch_path, watch_patterns):
    """ Watches a path and runs the command whenever files/directories change

    Note that this featrue is highly experimental and is known to fail from
    time to time.

    The ``cmd`` argument can be either an iterable or a string.

    This function will set up watchdog_ to monitor a path specified using the
    ``watch_path`` argument with ``watch_pattern`` glob pattern filter, and run
    the command each time there is a change. The commands are run in blocking
    mode using ``run()`` with ``wait`` flag, but the ``watch()`` function
    itself is non-blocking.

    The command is run at least once before path monitoring starts.

    Note that the function will raise a ``RuntimeError`` exception if watchdog
    is not installed or cannot be imported.

    The function's return value is a watchdog observer.

    .. _watchdog: https://pypi.python.org/pypi/watchdog

    """

    if nowatch:
        raise RuntimeError('Watchdog is not installed.')

    run(cmd, True)

    watch_path = os.path.abspath(os.path.normpath(watch_path))

    print('Watching %s' % watch_path)

    if platform.system() == 'Windows':
        observer = WindowsApiObserver()
    else:
        observer = Observer()

    handler = PatternWatcher(
        fn=lambda: run(cmd, True),
        patterns=watch_patterns
    )

    observer.schedule(handler, os.path.normpath(watch_path), recursive=True)
    observer.start()
    return observer


def wait_for_interrupt(*children):
    """ Waits for keyboard interrupt and terminates child processes

    This function takes any number of child processes or watchdog observers as
    positional arguments and waits for keyboard interrupt, terminating the
    processes and stopping observers.

    A prompt 'Press Ctrl-C to terminate' will be shown when it's called.

    This function is blocking. It will not return at any time. It will cause
    the parent script to exist with 0 status on interrupt.

    Note that this function does not check if arguments are child processes or
    observers. It will simply terminate/stop anything it can and exit.

    It can be used (and it is meant to be used) with functions like ``run()``
    and ``watch()``.

    Example::

        >>> wait_for_interrupt(run('compass watch'))
        Press Ctrl-C to terminate

    """

    print('Press Ctrl-C to terminate')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for c in children:
            if hasattr(c, 'terminate'):
                c.terminate()
            if hasattr(c, 'stop'):
                c.stop()
        sys.exit(0)


class Make(object):
    """ Build management class

    This class is used to organize your build files called zorofiles. The
    instances are callable, and the build file is executed by calling them.

    This class is meant to be subclassed and not used directly. When
    subclassing ``Make``, be sure to add a docstring to your subclass since it
    is used as a help message when running the build script without any options
    or with the -h switch.

    To define build targets, simply add methods to your subclass. Each method
    may have a docstring which is used to display help message when listing
    targets using the -l switch.

    A typical example of a build script would look like this (triple-quotes are
    replaced with double quotes since the example appears in docstrings)::

        class MyBuild(Make):
            "" Build my project ""

            def target(self):
                "" Do something here ""
                pass

        if __name__ == '__main__':
            MyBuild()()

    The class is called twice, once to create an instance, and once to call the
    instance.

    """

    _args = None
    _options = None

    def __init__(self):
        """ Create the parser object

        The sole purpose of the constructor is to build the parser object. If
        you wish to customize the process, you should overload the constructor
        and build your own parser. The parser object is expected to implement
        the ``optparse`` API and be added to the instance as ``_parser``
        attribute.

        An idiomatic way to customize the parser would be to call the
        superclass' constructor and then manipulate the parser object. For
        instance::

            class MyBuild(Make):
                "" Build my project ""

                def __init__(self):
                    super(MyBuild, self).__init__()
                    self._parser.add_option('-q', '--quiet',
                                            action='store_false', ...)

        Since all arguments and options are passed to the build target methods,
        you should add all desired options here.

        """
        doc = self.__doc__ or ''
        self._parser = optparse.OptionParser(
            usage='%prog TARGET [TARGET...] [options]',
            epilog=' '.join([l.strip() for l in doc.split('\n')])
        )
        self._parser.add_option('-l', '--list', action='store_true',
                                help='list all available targets')

    def __call__(self):
        """ Execute the build

        Calling the instance parses all the command line options and arguments
        passed to the script, and has three possible outcomes depending on
        them. If no target (first positional argument) is passed, it will
        either print full usage instructions or a list of targets (if -l)
        switch is passed. If the target argument is present, the specified
        target is executed. Finally, if the target name is there, but the
        instance does not define such a target, an error is shown, and the
        script exists with status code 1.

        """

        (options, args) = self._parser.parse_args()
        self._options = options
        self._args = args
        if options.list is True:
            self._parser.print_usage()
            print('Available targets:\n')
            print(self._list())
        elif len(args):
            target = args.pop(0)
            if hasattr(self, target):
                method = getattr(self, target)
                print('Running task: %s' % method.__name__)
                method()
            else:
                err("No target with name '%s'.\nRun this script without "
                    'arguments to see a list of targets.\n' % target, 1)
        else:
            self._parser.print_help()

    def _list(self):
        """ Return a formatted list of targets

        This method is an internal helper method. You generally shouldn't need
        to overload this method except for purely cosmetic purposes.

        """

        targets = []
        for name in dir(self):
            if not name.startswith('_'):
                target = getattr(self, name)
                docs = target.__doc__ or ' undocumented'
                docs = docs.split('\n')[0].strip()
                targets.append('%12s: %s' % (name, docs))
        return '\n'.join(targets)

