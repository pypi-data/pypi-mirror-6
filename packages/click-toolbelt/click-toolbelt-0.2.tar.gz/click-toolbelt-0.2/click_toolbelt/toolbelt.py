# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from click_toolbelt import __namespace__, __version__


class ClickToolbelt(App):
    def __init__(self):
        super(ClickToolbelt, self).__init__(
            description='Tools for working with click packages',
            version=__version__,
            command_manager=CommandManager(__namespace__))


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    toolbelt = ClickToolbelt()
    return toolbelt.run(args)


if __name__ == '__main__':
    args = sys.argv[1:]
    sys.exit(main(args))
