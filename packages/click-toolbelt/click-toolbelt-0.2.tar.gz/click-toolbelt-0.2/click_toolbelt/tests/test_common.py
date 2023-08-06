# Copyright 2014 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import os
import tempfile
from unittest import TestCase

from mock import Mock, call, patch
from requests_oauthlib import OAuth1Session

from click_toolbelt.common import ClickToolbeltCommand, retry
from click_toolbelt.compat import ConfigParser


class BaseClickToolbeltCommandTestCase(TestCase):
    command_class = ClickToolbeltCommand

    def setUp(self):
        super(BaseClickToolbeltCommandTestCase, self).setUp()
        app = None
        args = None
        self.command = self.command_class(app, args)

    def get_temporary_file(self):
        return tempfile.NamedTemporaryFile()


class ClickToolbeltCommandTestCase(BaseClickToolbeltCommandTestCase):

    def test_take_action(self):
        self.assertEqual(self.command.take_action(None), None)


class GetConfigTestCase(BaseClickToolbeltCommandTestCase):

    def setUp(self):
        super(GetConfigTestCase, self).setUp()
        cfg_file = self.get_temporary_file()
        self.filename = cfg_file.name
        patcher = patch('click_toolbelt.common.os.path.join')
        mock_join = patcher.start()
        mock_join.return_value = self.filename
        self.addCleanup(patcher.stop)

        # make sure env is not overwritten
        patcher = patch.object(os, 'environ', {})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_config_with_no_existing_file(self):
        data = self.command.get_config()
        self.assertEqual(data, {})

    def test_get_config_with_no_existing_section(self):
        cfg = ConfigParser()
        cfg.add_section('some.domain')
        cfg.set('some.domain', 'foo', '1')
        cfg.write(open(self.filename, 'w'))

        data = self.command.get_config()
        self.assertEqual(data, {})

    def test_get_config(self):
        cfg = ConfigParser()
        cfg.add_section('login.ubuntu.com')
        cfg.set('login.ubuntu.com', 'foo', '1')
        cfg.write(open(self.filename, 'w'))

        data = self.command.get_config()
        self.assertEqual(data, {'foo': '1'})


class GetOAuthSessionTestCase(BaseClickToolbeltCommandTestCase):

    def setUp(self):
        super(GetOAuthSessionTestCase, self).setUp()
        patcher = patch(
            'click_toolbelt.common.ClickToolbeltCommand.get_config')
        self.mock_get_config = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_oauth_session_when_no_config(self):
        self.mock_get_config.return_value = {}
        session = self.command.get_oauth_session()
        self.assertIsNone(session)

    def test_get_oauth_session_when_partial_config(self):
        self.mock_get_config.return_value = {
            'consumer_key': 'consumer-key',
            'consumer_secret': 'consumer-secret',
        }
        session = self.command.get_oauth_session()
        self.assertIsNone(session)

    def test_get_oauth_session(self):
        self.mock_get_config.return_value = {
            'consumer_key': 'consumer-key',
            'consumer_secret': 'consumer-secret',
            'token_key': 'token-key',
            'token_secret': 'token-secret',
        }
        session = self.command.get_oauth_session()
        self.assertIsInstance(session, OAuth1Session)
        self.assertEqual(session.auth.client.client_key, 'consumer-key')
        self.assertEqual(session.auth.client.client_secret, 'consumer-secret')
        self.assertEqual(session.auth.client.resource_owner_key, 'token-key')
        self.assertEqual(session.auth.client.resource_owner_secret,
                         'token-secret')


class RetryDecoratorTestCase(TestCase):

    def target(self, *args, **kwargs):
        return dict(args=args, kwargs=kwargs)

    def test_retry(self):
        result, aborted = retry()(self.target)()
        self.assertEqual(result, dict(args=(), kwargs={}))
        self.assertEqual(aborted, False)

    @patch('click_toolbelt.common.time.sleep')
    def test_retry_small_backoff(self, mock_sleep):
        mock_terminator = Mock()
        mock_terminator.return_value = False

        delay = 0.001
        result, aborted = retry(mock_terminator, retries=2,
                                delay=delay)(self.target)()

        self.assertEqual(result, dict(args=(), kwargs={}))
        self.assertEqual(aborted, True)
        self.assertEqual(mock_terminator.call_count, 3)
        self.assertEqual(mock_sleep.mock_calls, [
            call(delay),
            call(delay * 2),
        ])

    def test_retry_abort(self):
        mock_terminator = Mock()
        mock_terminator.return_value = False
        mock_logger = Mock()

        result, aborted = retry(mock_terminator, delay=0.001, backoff=1,
                                logger=mock_logger)(self.target)()

        self.assertEqual(result, dict(args=(), kwargs={}))
        self.assertEqual(aborted, True)
        self.assertEqual(mock_terminator.call_count, 4)
        self.assertEqual(mock_logger.warning.call_count, 3)

    def test_retry_with_invalid_retries(self):
        for value in (0.1, -1):
            with self.assertRaises(ValueError) as ctx:
                retry(retries=value)(self.target)
            self.assertEqual(
                str(ctx.exception),
                'retries value must be a positive integer or zero')

    def test_retry_with_negative_delay(self):
        with self.assertRaises(ValueError) as ctx:
            retry(delay=-1)(self.target)
        self.assertEqual(str(ctx.exception),
                         'delay value must be positive')

    def test_retry_with_invalid_backoff(self):
        for value in (-1, 0, 0.1):
            with self.assertRaises(ValueError) as ctx:
                retry(backoff=value)(self.target)
            self.assertEqual(str(ctx.exception),
                             'backoff value must be a positive integer')
