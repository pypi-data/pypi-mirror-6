# Copyright 2014 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
import os
import tempfile
from collections import namedtuple
from unittest import TestCase

from mock import (
    ANY,
    DEFAULT,
    patch,
)
from requests import Response

from click_toolbelt import __namespace__
from click_toolbelt.constants import (
    UBUNTU_SSO_API_ROOT_URL,
)
from click_toolbelt.register import (
    Register,
)
from click_toolbelt.tests.test_common import ClickToolbeltCommandBaseTestCase


class BaseRegisterCommandTestCase(ClickToolbeltCommandBaseTestCase, TestCase):
    command_class = Register

    def setUp(self):
        super(BaseRegisterCommandTestCase, self).setUp()

        # setup patches
        mock_environ = {
            'UBUNTU_SSO_API_ROOT_URL': UBUNTU_SSO_API_ROOT_URL,
        }
        patcher = patch('click_toolbelt.register.os.environ', mock_environ)
        patcher.start()
        self.addCleanup(patcher.stop)


class RegisterAppTestCase(BaseRegisterCommandTestCase):

    def setUp(self):
        super(RegisterAppTestCase, self).setUp()

        name = 'click_toolbelt.common.ClickToolbeltCommand.get_oauth_session'
        patcher = patch(name)
        mock_session = patcher.start()
        self.mock_get = mock_session.return_value.get
        self.mock_post = mock_session.return_value.post
        self.addCleanup(patcher.stop)

        self.data = {
            'upload_id': 'some-valid-upload-id',
            'binary_filesize': 123456,
            'source_uploaded': False,
        }

        patcher = patch.multiple(
            'click_toolbelt.common',
            SCAN_STATUS_POLL_DELAY=0.0001)
        patcher.start()
        self.addCleanup(patcher.stop)

    @patch('click_toolbelt.register.Register.get_oauth_session')
    def test_register_app_with_invalid_oauth_session(self,
                                                     mock_get_oauth_session):
        mock_get_oauth_session.return_value = None
        response = self.command.register_app(self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': ['No valid credentials found.'],
            'application_url': '',
        })

    def test_register_app_uses_environment_variables(self):
        with patch.dict(os.environ,
                        MYAPPS_API_ROOT_URL='http://example.com'):
            register_url = 'http://example.com/click-app/'
            data = {
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
            }
            self.command.register_app(self.data)
            self.mock_post.assert_called_once_with(
                register_url, data=data, files=[])

    def test_register_app(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/'
        }

        mock_status_response = self.mock_get.return_value
        mock_status_response.ok = True
        mock_status_response.json.return_value = {
            'completed': True
        }

        response = self.command.register_app(self.data)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'application_url': '',
        })

    def test_register_app_error_response(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = False
        mock_response.reason = '500 INTERNAL SERVER ERROR'
        mock_response.text = 'server failure'

        response = self.command.register_app(self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': ['server failure'],
            'application_url': '',
        })

    def test_register_app_handle_malformed_response(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {}

        response = self.command.register_app(self.data)
        err = KeyError('status_url')
        self.assertEqual(response, {
            'success': False,
            'errors': [str(err)],
            'application_url': '',
        })

    def test_register_app_with_errors_during_scan(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/'
        }

        mock_status_response = self.mock_get.return_value
        mock_status_response.ok = True
        mock_status_response.json.return_value = {
            'completed': True,
            'message': 'some error',
            'application_url': 'http://example.com/myapp',
        }

        response = self.command.register_app(self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': ['some error'],
            'application_url': 'http://example.com/myapp'
        })

    def test_register_app_poll_status(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/'
        }

        response_not_completed = Response()
        response_not_completed.status_code = 200
        response_not_completed.encoding = 'utf-8'
        response_not_completed._content = json.dumps(
            {'completed': False, 'application_url': ''}).encode('utf-8')
        response_completed = Response()
        response_completed.status_code = 200
        response_completed.encoding = 'utf-8'
        response_completed._content = json.dumps(
            {'completed': True,
             'application_url': 'http://example.org'}).encode('utf-8')
        self.mock_get.side_effect = [
            response_not_completed,
            response_not_completed,
            response_completed,
        ]
        response = self.command.register_app(self.data)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'application_url': 'http://example.org',
        })
        self.assertEqual(self.mock_get.call_count, 3)

    def test_register_app_ignore_non_ok_responses(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/',
        }

        ok_response = Response()
        ok_response.status_code = 200
        ok_response.encoding = 'utf-8'
        ok_response._content = json.dumps(
            {'completed': True}).encode('utf-8')
        nok_response = Response()
        nok_response.status_code = 503

        self.mock_get.side_effect = [nok_response, nok_response, ok_response]
        response = self.command.register_app(self.data)
        self.assertEqual(response, {
            'success': True,
            'errors': [],
            'application_url': '',
        })
        self.assertEqual(self.mock_get.call_count, 3)

    def test_register_app_abort_polling(self):
        mock_response = self.mock_post.return_value
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'status_url': 'http://example.com/status/',
        }

        mock_status_response = self.mock_get.return_value
        mock_status_response.ok = True
        mock_status_response.json.return_value = {
            'completed': False
        }
        response = self.command.register_app(self.data)
        self.assertEqual(response, {
            'success': False,
            'errors': [
                'Package scan took too long.',
                'Please check the status later at: '
                'http://example.com/status/.',
            ],
            'application_url': '',
        })

    def test_register_app_with_metadata(self):
        self.command.register_app(self.data,
                                  metadata={'changelog': 'some changes',
                                            'tagline': 'a tagline'})
        self.mock_post.assert_called_once_with(
            ANY,
            data={
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
                'changelog': 'some changes',
                'tagline': 'a tagline',
            },
            files=[],
        )

    def test_register_app_ignore_special_attributes_in_metadata(self):
        self.command.register_app(
            self.data, metadata={
                'changelog': 'some changes',
                'tagline': 'a tagline',
                'upload_id': 'my-own-id',
                'binary_filesize': 0,
                'source_uploaded': True,
            })
        self.mock_post.assert_called_once_with(
            ANY,
            data={
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
                'changelog': 'some changes',
                'tagline': 'a tagline',
            },
            files=[],
        )

    @patch('click_toolbelt.common.open')
    def test_register_app_with_icon(self, mock_open):
        with tempfile.NamedTemporaryFile() as icon:
            mock_open.return_value = icon

            self.command.register_app(
                self.data, metadata={
                    'icon_256': icon.name,
                }
            )
            self.mock_post.assert_called_once_with(
                ANY,
                data={
                    'updown_id': self.data['upload_id'],
                    'binary_filesize': self.data['binary_filesize'],
                    'source_uploaded': self.data['source_uploaded'],
                },
                files=[
                    ('icon_256', icon),
                ],
            )

    @patch('click_toolbelt.common.open')
    def test_register_app_with_screenshots(self, mock_open):
        screenshot1 = tempfile.NamedTemporaryFile()
        screenshot2 = tempfile.NamedTemporaryFile()
        mock_open.side_effect = [screenshot1, screenshot2]

        self.command.register_app(
            self.data, metadata={
                'screenshots': [screenshot1.name, screenshot2.name],
            }
        )
        self.mock_post.assert_called_once_with(
            ANY,
            data={
                'updown_id': self.data['upload_id'],
                'binary_filesize': self.data['binary_filesize'],
                'source_uploaded': self.data['source_uploaded'],
            },
            files=[
                ('screenshots', screenshot1),
                ('screenshots', screenshot2),
            ],
        )


class RegisterCommandTestCase(BaseRegisterCommandTestCase):

    def setUp(self):
        super(RegisterCommandTestCase, self).setUp()

        patcher = patch('click_toolbelt.register.Register.log')
        self.mock_log = patcher.start()
        self.addCleanup(patcher.stop)

        self.parsed_args = namedtuple(
            'parsed_args',
            'binary_filename, source_filename, metadata_filename')
        self.args = self.parsed_args('binary', None, None)

    def test_parser(self):
        parser = self.command.get_parser(__namespace__)
        # binary_filename is required
        self.assertEqual(parser._actions[1].dest, 'binary_filename')
        self.assertTrue(parser._actions[1].required)
        # source_filename is optional
        self.assertEqual(parser._actions[2].dest, 'source_filename')
        # this is a positional argument
        self.assertEqual(parser._actions[2].option_strings, [])
        self.assertFalse(parser._actions[2].required)
        self.assertEqual(parser._actions[3].dest, 'source_filename')
        # this is a named argument
        self.assertEqual(parser._actions[3].option_strings, ['--source'])
        self.assertFalse(parser._actions[3].required)
        # metadata_filename is optional
        self.assertEqual(parser._actions[4].dest, 'metadata_filename')
        # this is a positional argument
        self.assertEqual(parser._actions[4].option_strings, [])
        self.assertFalse(parser._actions[4].required)
        self.assertEqual(parser._actions[5].dest, 'metadata_filename')
        # this is a named argument
        self.assertEqual(parser._actions[5].option_strings, ['--metadata'])
        self.assertFalse(parser._actions[5].required)

    def test_take_action(self):
        binary_filename = self.args.binary_filename
        source_filename = self.args.source_filename

        with patch.multiple(self.command, upload_files=DEFAULT,
                            register_app=DEFAULT):

            self.command.take_action(self.args)

            self.command.upload_files.assert_called_once_with(
                binary_filename, source_filename=source_filename)
            self.command.register_app.assert_called_once_with(
                self.command.upload_files.return_value,
                metadata={})
            self.mock_log.info.assert_any_call(
                'Application registered successfully.'
            )

    def test_take_action_with_metadata_file(self):
        mock_metadata_file = tempfile.NamedTemporaryFile()
        with open(mock_metadata_file.name, 'wb') as mock_file:
            data = json.dumps({'changelog': 'some changes'})
            mock_file.write(data.encode('utf-8'))
            mock_file.flush()

        with patch.multiple(self.command, upload_files=DEFAULT,
                            register_app=DEFAULT):

            args = self.parsed_args('binary', 'source',
                                    mock_metadata_file.name)
            self.command.take_action(args)

            self.command.upload_files.assert_called_once_with(
                'binary', source_filename='source')
            self.command.register_app.assert_called_once_with(
                self.command.upload_files.return_value,
                metadata={'changelog': 'some changes'})
            self.mock_log.info.assert_any_call(
                'Application registered successfully.'
            )

    def test_take_action_with_metadata_file_without_source_file(self):
        mock_metadata_file = tempfile.NamedTemporaryFile()
        with open(mock_metadata_file.name, 'wb') as mock_file:
            data = json.dumps({'changelog': 'some changes'})
            mock_file.write(data.encode('utf-8'))
            mock_file.flush()

        with patch.multiple(self.command, upload_files=DEFAULT,
                            register_app=DEFAULT):

            args = self.parsed_args('binary', None,
                                    mock_metadata_file.name)
            self.command.take_action(args)

            self.command.upload_files.assert_called_once_with(
                'binary', source_filename=None)
            self.command.register_app.assert_called_once_with(
                self.command.upload_files.return_value,
                metadata={'changelog': 'some changes'})
            self.mock_log.info.assert_any_call(
                'Application registered successfully.'
            )

    def test_take_action_with_error_during_upload(self):
        binary_filename = self.args.binary_filename
        source_filename = self.args.source_filename

        with patch.multiple(self.command, upload_files=DEFAULT,
                            register_app=DEFAULT):

            self.command.upload_files.return_value = {
                'success': False,
                'errors': ['some error']
            }

            self.command.take_action(self.args)

            self.command.upload_files.assert_called_once_with(
                binary_filename, source_filename=source_filename)
            self.assertFalse(self.command.register_app.called)
            self.mock_log.info.assert_any_call(
                'Upload failed:\n\n%s\n', 'some error')

    def test_take_action_with_error_during_registration(self):
        binary_filename = self.args.binary_filename
        source_filename = self.args.source_filename

        with patch.multiple(self.command, upload_files=DEFAULT,
                            register_app=DEFAULT):

            self.command.register_app.return_value = {
                'success': False,
                'errors': ['some error'],
            }

            self.command.take_action(self.args)

            self.command.upload_files.assert_called_once_with(
                binary_filename, source_filename=source_filename)
            self.command.register_app.assert_called_once_with(
                self.command.upload_files.return_value,
                metadata={})
            self.mock_log.info.assert_any_call(
                'Registration did not complete.')
            self.mock_log.info.assert_any_call(
                'Some errors were detected:\n\n%s\n\n',
                'some error')

    def test_take_action_shows_application_url(self):
        with patch.multiple(self.command, upload_files=DEFAULT,
                            register_app=DEFAULT):

            self.command.register_app.return_value = {
                'success': True,
                'errors': [],
                'application_url': 'http://example.com/',
            }

            self.command.take_action(self.args)

            self.mock_log.info.assert_any_call(
                'Please check out the application at: %s.\n',
                'http://example.com/')
