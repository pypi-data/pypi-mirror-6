# -*- coding: utf-8 -*-
from __future__ import print_function

from os.path import dirname, join, realpath, sep, abspath

import baker
from voodoo import render_skeleton

from .main import Clay, DEFAULT_HOST, DEFAULT_PORT


SKELETON = join(dirname(realpath(__file__)), 'skeleton')

SKELETON_HELP = """
    Done!
    Now go to %s, and do `clay run` to start the server.
"""


manager = baker.Baker()


@manager.command
def new(path='.', template=None):
    """Creates a new project
    """
    path = abspath(path.rstrip(sep))
    template = template or SKELETON
    render_skeleton(template, path, include_this=['.gitignore'])
    print(SKELETON_HELP % (path,))


@manager.command
def run(host=DEFAULT_HOST, port=DEFAULT_PORT, path='.'):
    """Run the development server
    """
    path = abspath(path)
    c = Clay(path)
    c.run(host=host, port=port)


# @manager.command
# def debug(host=DEFAULT_HOST, port=DEFAULT_PORT, path='.'):
#     """Like 'Run' but starting pudb on error
#     """
#     import sys
#     def on_error(type, value, tb):
#         import pudb
#         if sys.stderr.isatty() or sys.stdin.isatty():
#             return
#         pudb.pm()

#     sys.excepthook = on_error
#     run(host, port, path)


@manager.command
def build(pattern=None, path='.'):
    """Generates a static copy of the sources
    """
    path = abspath(path)
    c = Clay(path)
    c.build(pattern)


@manager.command
def version():
    """Returns the current Clay version
    """
    from clay import __version__
    print(__version__)


def main():
    manager.run()
