====
zoro
====

Before we introduce you to zoro, please do not confuse it with Zorro_ which is
a networking library that has nothing to do with this one.

The name 'zoro' comes from a Japanese onomatopoeic phrase 'zoro zoro' which
signifies a sound a horde makes as it goes somewhere.

Having to deal with a build process that involves both backend and frontend
code, transpiled languages like CoffeScript, LiveScript, LESS or Compass,
exotic configuration files or settings that need to be swapped before going
into production... The horde of tasks that need to be completed before a
project can be served to the masses can be hard to deal with without software
to help us. On the other hand, learning a complex build system may seem like a
chore.

Zoro tries to fill the gap between writing small (shell) scripts, and mastering
a full build system like Buildout. I chose Python for this task, not only
because I develop Python software, but also because of its vast standard
library that can simplify many tasks without pulling in dozens of third-party
libraries. Zoro is also a simple and pure Python module, so you do not need
anything other than the Python interpreter installed on your system. This makes
it not only easy to install, but also portable across platforms.

In fact, the ``zoro`` module itself does not hide any of the modules and
functions it imports from the standard library, so you can ``from zoro import
*`` to access them witout having to add many lines of imports. Further more,
though its API, zoro tries to stay as close to bare Python as possible. After
all, why invent a new language if there is already a good one (or ten).

.. contents::

License
=======

Zoro is released under MIT license. See the source code for copyright and
license.

Installation
============

You can install zoro frim PyPI as usual::

    easy_install zoro

or::

    pip install zoro

Basic concept
=============

Somewhat similar to GNU Make, zoro allows you to easily define build targets,
and run various commands within them. This is achieved through the use of
``zoro.Make`` class. Let's take a look at a real-life example of such a class
and discuss its usage. ::

    #!/usr/bin/env python

    from zoro import *


    class Targets(Make):
        """
        Build my project.
        """

        def __init__(self):
            super(Targets, self).__init__()
            self._parser.add_options('-k', '--key', help='API key',
                                     dest='api_key')

        def dev(self):
            """ start test runners, servers and compilers """
            wait_for_interrupt(
                run(node_local('lsc -cwbo static/js src/ls')),
                run('compass watch -c tools/compass.rb'),
                run(python('app/main'), env={'APPENV': 'development'}),
            )

        def test(self, args, options):
            """ run unit tests """
            wait_for_interrupt(
                watch(python('tools/run_tests'), '.', '*.py'),
            )

        def build(self):
            """ prepares the project for deployment """
            self.clean()
            copytree('app', 'build/app')
            copytree('static', 'build/static')
            patch('build/app/conf.py', lambda s: self._patch_key(s))
            cleanup('build', '*.pyc')
            run(python('tools/cachebust build/app/templates'), wait=True)

        def _patch_key(self, s):
            key = self._options.k.api_key
            if key is None:
                err('No API key specified', 1)
            return re.sub(r"API_KEY='[^']+'", "API_KEY='%s'" % key, s)


    if __name__ == '__main__':
        Targets()()


This file is usually saved as 'zorofile' in the project's root directory.  The
shebang line at the top of the file allows us to run this file without
explicitly naming the interpreter (on Linux and UNIX systems at least). On
Windows we also include a 'zorofile.cmd' file to go with it. The contents of
the file may look like this::

    @echo off
    python zorofile %*

Now we can start calling the zorofile directly.

Importing zoro functions
~~~~~~~~~~~~~~~~~~~~~~~~

Normally, when using zoro, we import everything from ``zoro`` module with::

    from zoro import *

This pulls in not only the functions and classes defined by zoro itself, but
also anything and evertyhing zoro itself imports. This includes (among other
things, the ``os`` module, ``sys``, ``time``, ``platform``, ``shlex``,
``datetime``, etc). For a full listing of what's imported, you should look at
the source code.

Targets class
~~~~~~~~~~~~~

The next thing we notice is the ``Targets`` class. It's a subclass of the
``zoro.Make`` class, and we use it to house all our build targets, as well as
any utility methods we might need.

The constructor
~~~~~~~~~~~~~~~

The constructor of the ``zoro.Make`` class builds a parser object (created by
``optparse`` module). The parser is used to define and parse command line
arguments passed to our zorofile. In our subclass, we augment the default
parser with a new option '-k', which we will use to pass a production API key
during the build process.

Parsed positional arguments and options are stored as ``_args`` and
``_options`` instance attributes respectively and can be access by all instance
methods.

Targets and utilities
~~~~~~~~~~~~~~~~~~~~~

Let's cover the utility methods first. In our example, we have one utility
method which replaces the API key in our configuration module. The reason we
made it an instance method instead of a function defined outside the class is
that this way we have access to all properties on the class, including the
``_options`` attribute mentioned in the previous section.

The reason utility methods are prefixed with an underscore is that methods
without a leading underscore will be treated as build targets.

You will also note that we are using the ``re`` module without explicitly
importing it. We can do that because it is already imported in the ``zoro``
module.

Apart from the constructor and the utility method, there are also three build
targets: 'dev', 'test', and 'build'. All three targets are normal Python
methods. They have docstrings of which the first lines are used in help message
when the zorofile is run with the '-l' switch.

The 'dev' target is used when we want to develop the application. It
facilitates live compilation of LiveScript_ and Compass_ code and runs our
application's built-in development server. This is achieved by using the
``zoro.run()`` function.

The ``zoro.run()`` function executes commands asyncrhonously by default. This
means that the function itself returns before the command exits. This is
convenient because the commands in the 'dev' target will run indefinitely until
they receive a keyboard interrupt.

The first command is passed to ``zoro.node_local()`` function. This function
constructs the correct path for the locally installed NodeJS_ dependencies. The
actual command to run is dependent on the platform we are on, and this function
also takes care of ironing out the differences.

Third command is a python script, so we are passing it to ``zoro.python()``
function, which prepends 'python' and appends the '.py' extension. You will
also notice that the third command uses an ``env`` keyword argument to the
``zoro.run()`` function. This allows us to override or add envionrment 
variables specifically for that command.

All three commands in the 'dev' target are wrapped in
``zoro.wait_for_interrupt()`` call. This function takes child process objects
or watchdog_ observers as positional arguments, and terminates them all when
the zorofile receives a keyboard interrupt. Because ``zoro.run()`` returns a
child process object for the command it executes, we can pass its return value
directly to ``zoro.wait_for_interrupt()``.

The second target, 'test', looks very similar to the 'dev' target, but it runs
its command using ``zoro.watch()`` instead of ``zoro.run()``. The
``zoro.watch()`` function takes three arguments. The first one is the same as
``zoro.run()``. The second argument is a path that should be monitored for
changes and the last argument is a glob pattern to use as a filter. Whenever a
file or directory under the monitored path, matching the specified glob
pattern, is modified, the command is executed. This allows us to rerun our
tests whenever we modify a Python module.

Finally, the 'build' target creates a 'build' directory and prepares the code
for deployment. It uses the ``shutil.copytree()`` function to copy the
directories into the target directory, calls ``zoro.patch()`` to patch the
configuration file with the help from the utility method, and uses
``zoro.cleanup()`` to remove unneeded files.

Running the targets
~~~~~~~~~~~~~~~~~~~

To run the targets, we need to call the instance of our ``Targets`` class. This
is done in an ``if`` block so that it is only run when the zorofile is called
directly.

API documentation
=================

There is no separate API documentation, but you will find the source code to be
well-documented. The code is less than 700 lines *with* inline documentation,
so you should just dig in. You will find examples for each function in the
docstrings.

Reporting bugs
==============

Please report any bugs to the project's `BitBucket bugtracker`_.

.. _Zorro: https://pypi.python.org/pypi/Zorro
.. _LiveScript: http://livescript.net/
.. _Compass: http://compass-style.org/
.. _watchdog: http://pythonhosted.org//watchdog/
.. _BitBucket bugtracker: https://bitbucket.org/brankovukelic/zoro/issues
