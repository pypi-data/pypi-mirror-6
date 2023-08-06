============
betterconfig
============

betterconfig provides a more convenient and extensible configuration language,
and a simpler interface built on python's builtin ConfigParser format, along
with a drastically simplified interface for loading configs.

Type Coercion Boilerplate Sucks
===============================

ConfigParser, like many config languages, treats all values as strings,
meaning that when you have configs like this:

::

    [config]
    foo = 1
    bar = a,list,of,strings
    baz = just a plain old string

you end up with boilerplate that looks like this:

::

    from ConfigParser import ConfigParser
    MAP = {
        'foo': int,
        'bar': lambda x: x.split(','),
        'baz': str,
    }
    c = ConfigParser()
    c.read('./foo.cfg')
    config = {k:MAP[k](v) for k,v in c.items('config')}

Don't you really wish you could just do this:

::

    [config]
    foo = 1
    bar = ['a', 'list', 'of', 'strings']
    baz = "just a plain old string"

and drop the map?

::

    import betterconfig
    config = betterconfig.load('./foo.cfg')['config']

betterconfig supports all literal types supported by ast.literal_eval_:
strings, numbers, tuples, lists, dicts, booleans, and None.

.. _ast.literal_eval: http://docs.python.org/2/library/ast.html#ast.literal_eval

More Flexibility in Config, Less Config by Module
=================================================

We wanted a config language that was as easy to use as a settings module in
django or flask (and nearly as extensible), but less magical to initialize,
and slightly safer than something like this:

::

    import importlib
    settings = importlib.import_module('settings')

So we want a config that can do stuff like this:

::

    top_level  = 'variables defined outside of sections'
    include    = ['./include.cfg', 'include.d/*.cfg']

    [section]
    namespaced = True

And we don't want to have to iterate sections or items, we really just want to
load it into a dict:

::

    import betterconfig
    settings = betterconfig.load('./fancy.cfg')

And if you're really in love with ``.`` notation, you can always do something
silly like make a module ``settings.py`` that does something magical like:

::

    import betterconfig
    globals().update(betterconfig.load('./fancy.cfg'))

Installing
==========

The betterconfig project lives on github_, and is available via pip_.

.. _github: https://github.com/axialmarket/betterconfig
.. _pip: https://pypi.python.org/pypi/betterconfig/0.3

Installing v0.3 From Pip
------------------------

::

    sudo pip install betterconfig==0.3

Installing v0.3 From Source
---------------------------

::

    curl https://github.com/axialmarket/betterconfig/archive/version_0.3.tar.gz | tar vzxf -
    cd betterconfig
    sudo python setup.py install

Running Tests
=============

The betterconfig tests require py.test, which can be installed via pip.

::

    sudo pip install pytest==2.5.2
    py.test test_betterconfig.py



Authors and Contributors
========================

| Matthew Story <matt.story@axial.net>
| Jon Rosebaugh <jon@inklesspen.com>
| Inspired By: http://stackoverflow.com/a/6209146
| Inspired By: http://stackoverflow.com/a/2819788
