#!/usr/bin/python
'''
betterconfig provides a more convenient and extensible configuration language,
and a simpler built on python's builtin ConfigParser format, along with a
drastically simplified interface for loading configs.

@version: 0.2
@author: Matt Story <matt.story@axial.net>

No More Type Coercion
---------------------

betterconfig provides typing support for a variety of python literals by way
of the ast module:

    [config]
    foo = 1
    bar = ['a', 'list', 'of', 'strings']
    baz = "just a plain old string"

The following types are supported: strings, numbers, tuples, lists, dicts,
booleans, and None.

Glob Includes
-------------

If the 'include' directive is specified in the sectionless part of the
configuration, betterconfig will glob expand each include and then include
them:

    # this
    include =  'includes/*.cfg'
    # or this
    include =  ['include/foo.cfg', '/etc/defaults.cfg']

You can include even from included configs.

Some Things to Know
-------------------

Values defined in a section with the same name as the 'default' keyword
argument passed to 'load' (default: '_') will be made available at sectionless
scope:

    [_]
    foo = 'bar'

Would yield:

    betterconfig.load('./foo.cfg')['foo'] # 'bar'


'''
import os
import ast
import glob
from ConfigParser import SafeConfigParser, RawConfigParser,\
                         MissingSectionHeaderError

######## BEGIN SECTIONLESS HACKS
class _Sectionless(object):
    '''Hack for sectionless config'''
    def __init__(self, file_, sect):
        self.__was_open, self.__file = self.__open(file_)
        self.__secthead = '[{}]'.format(sect)

    def __getattr__(self, attr):
        return getattr(self.__file, attr)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        if not self.__was_open:
            self.__file.close()

    def __open(self, file_):
        # this is all we really care about ... quack, quack
        if hasattr(file_, 'readline'):
            return True, file_
        return False, open(file_, 'r')

    def readline(self):
        '''The read interface used by ConfigParser'''
        if self.__secthead:
            try:
                return self.__secthead
            finally:
                self.__secthead = None

        return self.__file.readline()
######## END SECTIONLESS HACKS

def _id_and_dir(cfg_file):
    '''Return inode and dirname of open file-ish if they are available.
        cfg_file
         - file-ish type (file, StringIO)'''
    dir_name = os.path.dirname(getattr(cfg_file, 'name', ''))
    try:
        stat = os.fstat(cfg_file.fileno())
        return '-'.join([str(stat.st_ino), str(stat.st_dev)]), dir_name
    except AttributeError:
        return None, dir_name

def _expand_includes(include, cur_dir):
    '''Do a glob expansion on one or more included config files.
        include
         - one (basestr) or more (iterable) include globs to expand.
        cur_dir
         - cur_dir: directory to base relative include globs off of'''
    expanded = []
    include = [include] if isinstance(include, basestring) else include
    for glob_includes in include:
        # expand and sort to support 0001-style convention
        glob_includes = glob.glob(os.path.join(cur_dir, glob_includes))
        glob_includes.sort()
        expanded.extend(glob_includes)

    return expanded

def load(*cfgs, **kwargs):
    '''Load betterconfig config files into a python dict.
        cfgs
         - iterable of file-ish types (file, StringIO, etc)
        include='include'
         - name of the 'include' directive in a betterconfig file, to disable
           includes, send None
        default='default'
         - name used for default section, whose values are stored that the top
           level of the returned python dictionary.
        seen=set()
         - a set of seen cfg identifiers (inodes), to prevent infinitely
           recursive includes.
        raw=True
         - enables interpolation of %(tokens)s when falsy
        mapper=dict
         - type to use for the mapping.'''
    opts = { 'include': kwargs.pop('include', 'include'),
             'default': kwargs.pop('default', '_'),
             'seen': kwargs.pop('seen', set()),
             'raw': kwargs.pop('raw', True),
             'mapper': kwargs.pop('mapper', dict) }
    if kwargs:
        raise TypeError('{} is an invalid keyword argument'\
                        'for this function'.format(kwargs.keys()[0]))

    compiled_config = opts['mapper']()
    for cfg in cfgs:
        includes = []
        with _Sectionless(cfg, opts['default']) as cfg_file:
            # prevent infinite include recursion
            id_, cfg_dir = _id_and_dir(cfg_file)
            if id_ in opts['seen']:
                continue
            elif id_ is not None:
                opts['seen'].add(id_)

            parser = RawConfigParser() if opts['raw'] else SafeConfigParser()
            parser.optionxform = lambda x: x #ConfigParser calls lower() on each key.
            parser.readfp(cfg_file)

            for sect in parser.sections():
                sect_config = compiled_config
                if sect != opts['default']:
                    sect_config = compiled_config.setdefault(sect, {})

                for key,val in parser.items(sect):
                    val = ast.literal_eval(val)
                    if sect == opts['default'] and key == opts['include']:
                        includes.extend(_expand_includes(val, cfg_dir))
                    else:
                        sect_config[key] = val

        # after we've finished one file, overlay any includes
        if includes:
            compiled_config.update(load(*includes, **opts))

    return compiled_config

__all__ = ['load']

if __name__ == '__main__':  # pragma: no cover
    import sys
    import pprint
    pprint.pprint(load(*(sys.argv[1:] or [sys.stdin])))
