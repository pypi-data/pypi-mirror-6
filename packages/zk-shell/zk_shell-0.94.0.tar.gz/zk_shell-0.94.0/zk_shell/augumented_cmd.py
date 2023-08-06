""" decorate cmd with some convenience stuff """
from __future__ import print_function

import argparse
import cmd
from functools import partial, wraps
import os
import shlex
import sys


class BasicParam(object):
    """ a labeled param """
    def __init__(self, label):
        self.label = label

    @property
    def pretty_label(self):
        """ the label as it should be displayed in messages """
        return self.label


class Required(BasicParam):
    """ a required param """
    pass


class Optional(BasicParam):
    """ an optional param """
    @property
    def pretty_label(self):
        return "<%s>" % (self.label)


class Multi(BasicParam):
    """ a multi param """
    pass


class BooleanOptional(BasicParam):
    """ an optional boolean param """
    def __init__(self, label, default=False):
        super(BooleanOptional, self).__init__(label)
        self.default = default


class IntegerOptional(BasicParam):
    """ an optional integer param """
    def __init__(self, label, default=0):
        super(IntegerOptional, self).__init__(label)
        self.default = default


class BooleanAction(argparse.Action):
    """ used to parse boolean string params """
    def __call__(self, parser, namespace, values, option_string=None):
        value = values if type(values) == bool else values.lower() == "true"
        setattr(namespace, self.dest, value)


class ShellParser(argparse.ArgumentParser):
    """ a cmdline parser useful for implementing shells """

    class ParserException(Exception):
        """ parser generated exception """
        pass

    @classmethod
    def from_params(cls, params):
        """ generate an instance from a list of params """
        parser = cls()
        for param in params:
            if isinstance(param, Required):
                parser.add_argument(param.label)
            elif isinstance(param, Optional):
                parser.add_argument(param.label, nargs="?", default="")
            elif isinstance(param, BooleanOptional):
                parser.add_argument(param.label, nargs="?", default=param.default, action=BooleanAction)
            elif isinstance(param, IntegerOptional):
                parser.add_argument(param.label, nargs="?", default=param.default, type=int)
            elif isinstance(param, Multi):
                parser.add_argument(param.label, nargs="+")
            else:
                raise ValueError("Unknown parameter type: %s" % (param))
        parser.set_valid_params(" ".join(param.pretty_label for param in params))
        return parser

    @property
    def valid_params(self):
        """ a string with the valid params for this parser instance """
        return self.__dict__['_valid_params']

    def set_valid_params(self, params):
        """ sets the string list of valid params """
        self.__dict__['_valid_params'] = params

    def error(self, message):
        """ handle an error raised by ArgumentParser """
        full_msg = "Wrong params: %s, expected: %s" % (message, self.valid_params)
        raise self.ParserException(full_msg)


def interruptible(func):
    """ handle KeyboardInterrupt for func """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            pass
    return wrapper


def ensure_params_with_parser(parser, func):
    """ parse args with parser and run func """
    @wraps(func)
    def wrapper(*args):
        try:
            params = parser.parse_args(shlex.split(args[1]))
            return func(args[0], params)
        except ShellParser.ParserException as ex:
            print(ex)
    return wrapper


def ensure_params(*params):
    """ decorates with a Parser built from params """
    parser = ShellParser.from_params(params)
    return partial(ensure_params_with_parser, parser)


class AugumentedCmd(cmd.Cmd):
    """ extends cmd.Cmd """
    curdir = "/"

    def __init__(self, hist_file_name=None, setup_readline=True):
        cmd.Cmd.__init__(self)

        if setup_readline:
            self._setup_readline(hist_file_name)

    def default(self, line):
        args = shlex.split(line)
        if len(args) > 0 and not args[0].startswith("#"):  # ignore commented lines, ala Bash
            print("Unknown command: %s" % (args[0]))

    def emptyline(self):
        pass

    def run(self, intro=None):
        self.intro = intro
        self.cmdloop()

    def _exit(self, newline=True):
        if newline:
            print("")
        sys.exit(0)

    def resolve_path(self, path):
        """
        transform a given relative or abbrev path into a fully resolved one

        i.e.:
          ''          -> /full/current/dir
          '.'         -> /full/current/dir
          '..'        -> /full/parent/dir
          'some/path' -> /full/some/path
        """
        if path in ["", "."]:
            path = self.curdir
        elif path == "..":
            path = os.path.dirname(self.curdir)

        if not path.startswith("/"):
            path = "%s/%s" % (self.curdir.rstrip("/"), path.rstrip("/"))

        return os.path.normpath(path)

    def update_curdir(self, dirpath):
        if dirpath == "..":
            if self.curdir == "/":
                dirpath = "/"
            else:
                dirpath = os.path.dirname(self.curdir)
        elif not dirpath.startswith("/"):
            prefix = self.curdir
            if prefix != "/":
                prefix += "/"
            dirpath = prefix + dirpath

        self.curdir = dirpath
        self.prompt = "%s%s> " % (self.state, dirpath)

    @property
    def state(self):
        return ""

    def _setup_readline(self, hist_file_name):
        try:
            import readline, atexit
        except ImportError:
            return

        if hist_file_name is None:
            return

        path = os.path.join(os.environ["HOME"], hist_file_name)
        try:
            readline.read_history_file(path)
        except IOError:
            pass
        atexit.register(readline.write_history_file, path)
