#!/usr/bin/env python
# coding: utf-8
"""
Script Command-Line Interface Parser

A CLI parser with a simple interface, wrapper of the standard module `getopt`.
The emphasis is on the use of a single set of natural option names from which 
short and long options are automatically derived.

Quick Start
-----------

The typical usage of the `script` module to parse command-line argument is
given by the source of an example document converter script. 
This `convert` script provides a command-line interface to a (not implemented)
Python function with the same name.
    
    #!/usr/bin/env python

    import script
    last = script.last
    
    def convert(filenames, format=None, verbosity=0, strict=False):
        raise NotImplementedError()

    def usage():
        print "usage:"
        print "convert", 
        print "[-h --help -fFORMAT --format=FORMAT -v --verbose -s --strict]", 
        print "FILENAMES"
    
    def main():
        spec = "help format= verbose strict" 
        options, filenames = script.parse(spec)
        if options.help:
            usage()
        else:
            format    = last(options.format)
            verbosity = len(options.verbose)
            strict    = bool(options.strict)
            convert(filenames, format, verbosity, strict)

    if __name__ == "__main__":
        main()

Assuming that the file is in your `$PATH`, the script can be called with:

    $ convert --format=html -v -v -s doc.txt

a command that would generate the Python API call:

    convert(["doc.txt"], format="html", verbosity=2, strict=True)


Option Specification List
-------------------------

The option specification list (`spec`) is a string that contains a sequence of
individual option specification, separated by whitespace, such as:

    >>> spec = "help v e_x_tract output= config=dict"

The structure of an individual option specification is 

    NAME [ = [TYPE] ]

where:

  - `NAME` is the option name. 

    The option is short if it is a single char, long otherwise. 
    A short option is automatically associated to a long option, 
    whose name is normally the first character of the long option name.
    When a character is enclosed by underscores in the long option name, 
    it is used as a short option name instead ; 
    in this case, the underscores are stripped from the final long option name.

  - `'='` (optional) is used to specify options that require an argument. 

  - `TYPE` (optional) refers to the type of the argument as a Python object.

For example:

  - `"help"` refers to `-h` and `--help` (and requires no argument),

  - `"v"` refers to `-v` (and required no argument),

  - `"e_x_tract"` refers to `-x` and `--extract` (and requires no argument),

  - `"output="` refers to `-o` and `--ouput` and requires a string argument,

  - `"config=dict"` refers to `-c` and `--config` and requires a `dict` argument.

Parsing of the Arguments
------------------------

**TODO**

Option Argument Type
--------------------

**TODO: ** Warning: typechecking vs type filtering (that we don't do): we
DONT parse 8 as a float or 8.0 as an int.

The typing rules may be summarized as follows: if an option specification is

`NAME =`
  : : the option argument is not interpreted but kept as a string.

`NAME = object`
  : : the option argument is interpreted (`eval` is applied) but not typechecked.

`NAME = TYPE`
  : : the option argument is interpreted (`eval` is applied) and typechecked 
    against `TYPE`.

Given those rules, you usually don't want to use `str` as a type. 
The specs `"output="` and `"output=str"` actually mean something different: 
the former spec will accept an input such as `-otext` or `-o'text with spaces'` 
while the latter would require `-o'"text"'` or `-o'"text with spaces"'` to 
achieve the same result.

Builtin or custom types may be used in the third form but custom types 
should then be added to this module to make it work. Note that the second
form is not really an extra rule but a special case of the third one as the 
typechecking of the argument is done with the `isinstance` against the 
prescribed type.
"""

# Python 2.7 Standard Library
import getopt
import re
import sys
import shlex

#
# Metadata
# ------------------------------------------------------------------------------
#
__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__version__ = "trunk"

#
# Options and Arguments Parser
# ------------------------------------------------------------------------------
#
def parse(spec, args=None):
     """
     Parse the command-line arguments according to the options specification.

     Arguments
     ---------

     `spec:`
       : a string, the option specification list.

         Refer to the the top-level documentation for a description of its syntax.

     `args:`
       : a list of strings, a single string or `None` (the default). 

         If a string is used it will be processed by `shlex.split`.
         If the argument is `None`, the list `sys.argv[1:]` is used.

 
     Returns
     -------

     `(options, args):`
       : `options` is an `Options` instance and `args` a list of strings. 

     """
     if args is None:
         args = sys.argv[1:]
     if isinstance(args, str):
         args = shlex.split(args)
     short_options, long_options = to_getopt(spec)
     options, args = getopt.getopt(args, short_options, long_options)
     return Options(options, info=parse_option_spec_list(spec)), args

#
# Options
# ------------------------------------------------------------------------------
#

class Options(list):
    def __init__(self, iterable, info):
        self._info = info
        options = []
        for name, value in iterable:
            for short, long, type in info:
                if ("-" + short) == name or ("--" + (long or "")) == name:
                    if type:
                        if type != raw:
                            try:
                                value = eval(value)
                            except Exception:
                                raise # TODO: manage this situation.
                            if not isinstance(value, type):
                                error = "{0!r} is not a {1!s} instance" 
                                raise TypeError(error.format(value, type.__name__))
                    else:
                        value = None
                        break
            options.append((name, value))
        list.__init__(self, options)

    def __getattr__(self, name):
        shorts =  [short for short, _____, _ in self._info if short is not None]
        longs  =  [long  for _____, long , _ in self._info if long  is not None]
        if name not in shorts and name not in longs:
            raise AttributeError("option {0!r} not found.".format(name))
        else:
            return self._find(name)

    def _find(self, name):
        short = None
        keys = []
        if len(name) == 1:
            short = name
            for _short, _long, _ in self._info:
                if _short == short:
                    long = _long
        else:
            long = name
            for _short, _long, _ in self._info:
                if _long == long:
                    short = _short
        if short:
            keys.append("-" + short)
        if long:
            keys.append("--" + long)
        values = []
        for key, value in self:
            if key in keys:
                values.append(value)
        return values        

def first(iterable):
    """
Return the first item in `iterable` or `None` if it is empty.

    >>> first([1, 2, 3])
    1
    >>> first([]) is None
    True
    """
    for item in iterable:
        return item


def last(iterable):
    """
Return the last item in `iterable` or `None` if it is empty.

    >>> last([1, 2, 3])
    3
    >>> last([]) is None
    True
    """
    item = None
    for item in iterable:
        pass
    return item

#
# Internals
# ------------------------------------------------------------------------------
#

class raw(str):
    pass

def parse_option_spec_list(spec):
    """
Return a list of `(short, long, type)` option spec items.

Arguments
---------

`spec:`
  : an option specification list ; refer to the module-level documentation for
    details.

Returns
-------

`options:`
  : a list of `(short, long, type)` items where:

      - `short` is the option short name,
      - `long` is the option long name or `None`,
      - `type` is the type of the option argument or `raw` if the option
        is not explicitely typed. If the option requires no value, `type` is 
        `None`.

For example:

    >>> spec = "help v e_x_tract output= config=dict"
    >>> for short, long, type in parse_option_spec_list(spec):
    ...     s = ("-" + short)
    ...     l = ("--" + long) if long else ""
    ...     t = type.__name__ if type else "" 
    ...     print "{0:<2} | {1:<9} | {2:<4}".format(s, l, t)
    -h | --help    |     
    -v |           |     
    -x | --extract |     
    -o | --output  | raw 
    -c | --config  | dict
    """
    options = []
    spec_list = spec.split()    
    for option_spec in spec_list:
        parts = option_spec.split("=")
        name = parts[0]
        if len(name) == 1:
            short = name
            long = None
        else:
            match = re.search("_([a-zA-Z])_", name)
            if match:
                short = match.groups()[0]
                long = name.replace("_", "")
            else:
                short = name[0]
                long = name
        if len(parts) == 2:
            type = parts[1]
            if type:
                type = eval(type)
            else:
                type = raw 
        else:
            type = None
        for _short, _long, _ in options:
            if short == _short:
                error = "the short option {0!r} is defined several times."
                raise ValueError(error.format(short))
            if long is not None and long == _long:
                error = "the long option {0!r} is defined several times."
                raise ValueError(error.format(long))
        else:
            options.append((short, long, type))
    return options
            
def to_getopt(spec):
    """
Convert a script options spec into an `Options` object consistent with the 
conventions of `getopt.getopt`.

For example:

    >>> to_getopt("help output= e_x_tract")
    ('ho:x', ['help', 'output=', 'extract'])
"""
    getopt_short = ""
    getopt_long  = []
    for short, long, type in parse_option_spec_list(spec):
        has_arg = bool(type)
        getopt_short += short + has_arg * ":"
        if long:
            getopt_long.append(long + has_arg * "=")
    return getopt_short, getopt_long

#
# Script Entry Point
# ------------------------------------------------------------------------------
#

def main():
    """
    Doctest this module.
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    main()

