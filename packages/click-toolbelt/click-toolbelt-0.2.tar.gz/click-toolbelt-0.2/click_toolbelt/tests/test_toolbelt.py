# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import sys
from unittest import TestCase

from mock import patch

from click_toolbelt import __version__
from click_toolbelt.toolbelt import ClickToolbelt, main


class ClickToolbeltTestCase(TestCase):
    def test_constructor(self):
        toolbelt = ClickToolbelt()
        self.assertEqual(toolbelt.parser.description,
                         'Tools for working with click packages')
        self.assertEqual(toolbelt.command_manager.namespace, 'click_toolbelt')
        with self.assertRaises(SystemExit):
            self.assertIn(__version__, toolbelt.run(['--version']))


class MainTestCase(TestCase):
    def test_with_args(self):
        with patch('click_toolbelt.toolbelt.ClickToolbelt.run') as mock_run:
            args = []
            main(args)
            mock_run.assert_called_with(args)

    def test_no_args_uses_sys(self):
        with patch('click_toolbelt.toolbelt.ClickToolbelt.run') as mock_run:
            main()
            mock_run.assert_called_with(sys.argv[1:])
