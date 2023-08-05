"""Utils for the analog module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
from collections import Counter
import re


class AnalogArgumentParser(argparse.ArgumentParser):

    """ArgumentParser that reads multiple values per argument from files.

    Arguments read from files may contain comma or whitespace separated values.

    To read arguments from files create a parser with ``fromfile_prefix_chars``
    set::

        parser = AnalogArgumentParser(fromfile_prefix_chars='@')

    Then this parser can be called with argument files::

        parser.parse_args(['--arg1', '@args_file', 'more-args'])

    The argument files contain one argument per line. Arguments can be comma or
    whitespace separated on a line. For example all of this works::

        --format=nginx
        -o       table
        --verb   GET, POST, PUT
        --verb   PATCH
        --status 404, 500
        --path   /foo/bar
        --path   /baz
        --path-stats
        -t
        positional
        arg

    """

    _arg_separator = re.compile(r',|\s', re.UNICODE)
    _key_separator = re.compile(r'=|\s', re.UNICODE)

    def convert_arg_line_to_args(self, arg_line):
        """Comma/whitespace-split ``arg_line`` and yield separate attributes.

        Argument names defined at the beginning of a line (``-a``, ``--arg``)
        are repeated for each argument value in ``arg_line``.

        :param arg_line: one line of argument(s) read from a file
        :type arg_line: ``str``
        :returms: argument generator
        :rtype: generator

        """
        # split argument name from values
        key = None
        if arg_line.startswith('-'):
            key = self._key_separator.split(arg_line, 1)
            # key with value
            if len(key) > 1:
                key, arg_line = key
            # key only
            else:
                key = key[0]
                arg_line = ''
        # split arguments
        if arg_line:
            args = re.split(r',|\s', arg_line)
            for arg in args:
                if not arg.strip():
                    continue
                # include key for named arguments
                if key:
                    yield key
                yield arg
        # key only
        elif key:
            yield key


class PrefixMatchingCounter(Counter):

    """Counter-like object that increments a field if it has a common prefix.

    Example: "400", "401", "404" all increment a field named "4".

    """

    def inc(self, field):
        """Increment every field that starts with field by one."""
        for prefix in self.keys():
            if str(field).startswith(str(prefix)):
                self[prefix] += 1
