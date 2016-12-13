Clickfig: Simple Click-Based App Configuration
==============================================

`Click <http://click.pocoo.org/>`_ is a fantastic library for building CLI applications with composable commands, arguments, and options. However, sufficiently large applications can require a large amount of configuration options, making command line flags unwieldy. The common workaround to this is a configuration file. However, ``click`` doesn't have any built-in mechanisms for handling configuration files.

Hence ``clickfig``. Clickfig is a package that lets you simply and easily attach a configuration file (in ini or json format) to your click app. The configuration file is attached to a `group <http://click.pocoo.org/6/commands/>`_ as a ``command``, and allows for a simple CLI (somewhat inspired by ``git config``) for querying, updating, and deleting items in the configuration file.

Installation
------------

Just clone this repo, ``cd`` into wherever it was cloned, and do a ``python setup.py install``. Note that this will be up on PyPI (and installable via ``pip``) soon!

Example
-------

Let's look at ``examples/basic/basic_ini.py`` inside of this repo:

::

    import sys
    import click
    sys.path = ['../..'] + sys.path

    import clickfig

    cfg = clickfig.Config("./test.ini")


    @click.group()
    def main():
        pass


    clickfig.attach(main, cfg)

    if __name__ == "__main__":
        main()

Note that there are only two lines (other than setting ``sys.path``) that make this a minimal ``click`` app. The first:

::

    cfg = clickfig.Config("./test.ini")

tells ``clickfig`` to grab that configuration file, so that it can be used by ``clickfig``'s config file API. The second line:

::

    clickfig.attach(main, cfg)

builds a ``command`` that uses ``cfg`` to read and write items from/to ``test.ini``.

The contents of ``examples/basic/test.ini`` is:

::

    [foo]
    bar = baz
    blah = 2

    [section]
    stuff = things
    other = something else blah blah blah


And we see that there is a ``config`` command when we run ``basic_ini.py`` with a ``--help`` flag:

::

    $ python basic_ini.py --help
    Usage: basic_ini.py [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      config

Looking a bit closer at the ``config`` command:

::

    $ python basic_ini.py config --help
    Usage: basic_ini.py config [OPTIONS] [KEY] [VALUE]

    Options:
      --unset
      --help   Show this message and exit.

we can get items from the config file via specifying a key, set the value of a key by specifying both the key and value, and remove a key entirely via the ``--unset`` flag.

If no keys are specified, everything in the config file is displayed (this is one of many departures from the API in ``git config``):

::

    $ python basic_ini.py config
    section.other=something else blah blah blah
    section.stuff=things
    foo.bar=baz
    foo.blah=2

You can get specific values by specifying a key. Note that keys are represented in a hierarchical fashion, so ``x.y`` gets you the value of ``y`` in section ``x``, whereas ``x`` gets you everything in section ``x``:

::

    $ python basic_ini.py config foo
    foo.blah=2
    foo.bar=baz
    $ python basic_ini.py config foo.bar
    baz

And, as stated above, we can change these values:

::

    $ python basic_ini.py config foo.bar quux
    $ python basic_ini.py config foo.bar
    quux
    $ cat test.ini
    [foo]
    bar = quux
    blah = 2

    [section]
    stuff = things
    other = something else blah blah blah

Or, we can remove things altogether:

::

    $ python basic_ini.py config --unset foo.bar
    $ cat test.ini
    [section]
    other = something else blah blah blah
    stuff = things

    [foo]
    blah = 2

Of course, you can also access these values via the config file API, by getting at ``cfg`` (as defined above), and using the methods ``cfg.read``, ``cfg.write``, and ``cfg.unset``. It's also possible to specify different levels of configuration files--eg, ``local``, ``global``, and ``system,`` where ``local`` overrides ``global`` and ``global`` overrides ``system``.

This is still a bit of a work in progress. Feedback and pull requests are welcome!
