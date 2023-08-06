# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
from collections import namedtuple

from mock import patch
from requests import Response

from click_toolbelt import __namespace__
from click_toolbelt.constants import (
    UBUNTU_SSO_API_ROOT_URL,
)
from click_toolbelt.upload import (
    CLICK_UPDOWN_UPLOAD_URL,
    MYAPPS_API_ROOT_URL,
    Upload,
)
from click_toolbelt.tests.test_common import BaseClickToolbeltCommandTestCase


class BaseUploadCommandTestCase(BaseClickToolbeltCommandTestCase):
    command_class = Upload

    def setUp(self):
        super(BaseUploadCommandTestCase, self).setUp()
        self.app_name = 'namespace.package_name'
        self.app_archs = ['all']
        self.app_framework = 'ubuntu-sdk-13.10'
        self.app_version = '1'
        self.app_changelog = 'Initial version.'
        self.uploaded_callback_url = MYAPPS_API_ROOT_URL + 'click-uploaded/1/'

        # setup patches
        mock_environ = {
            'UBUNTU_SSO_API_ROOT_URL': UBUNTU_SSO_API_ROOT_URL,
        }
        patcher = patch('click_toolbelt.upload.os.environ', mock_environ)
        patcher.start()
        self.addCleanup(patcher.stop)


class GetUploadDataTestCase(BaseUploadCommandTestCase):

    def setUp(self):
        super(GetUploadDataTestCase, self).setUp()

        patcher = patch('click_toolbelt.upload.Upload.get_config')
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('click_toolbelt.upload.Upload.get_oauth_session')
        mock_session = patcher.start()
        self.mock_post = mock_session.return_value.post
        self.addCleanup(patcher.stop)

        mock_environ = {'MYAPPS_API_ROOT_URL': MYAPPS_API_ROOT_URL}
        patcher = patch('click_toolbelt.upload.os.environ', mock_environ)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_upload_data(self):
        expected = {
            'success': True,
            'errors': [],
            'binary_path': '/path/to/binary',
            'source_path': '/path/to/source',
            'signature': 'signature',
            'application_id': 1,
        }

        response = Response()
        response.status_code = 200
        response._content = json.dumps(expected).encode('utf-8')
        self.mock_post.return_value = response

        data = self.command.get_upload_data(self.app_name,
                                            self.app_version,
                                            self.app_changelog,
                                            self.app_archs,
                                            self.app_framework)
        self.assertEqual(data, expected)

    def test_get_upload_data_for_unknown_app(self):
        response = Response()
        response.status_code = 404
        response._content = (
            'The requested Click Package could not be found.'.encode('utf-8'))
        self.mock_post.return_value = response

        data = self.command.get_upload_data(self.app_name,
                                            self.app_version,
                                            self.app_changelog,
                                            self.app_archs,
                                            self.app_framework)
        self.assertEqual(data, {
            'success': False,
            'errors': ['The requested Click Package could not be found.']})

    def test_get_upload_data_resilient(self):
        self.mock_post.side_effect = Exception('some http error')

        data = self.command.get_upload_data(self.app_name,
                                            self.app_version,
                                            self.app_changelog,
                                            self.app_archs,
                                            self.app_framework)
        self.assertEqual(data, {'success': False,
                                'errors': ['some http error']})

    def test_get_upload_data_uses_default_myapps_url(self):
        upload_url = MYAPPS_API_ROOT_URL + "click-upload/%s/" % (
            self.app_name,)
        self.command.get_upload_data(
            self.app_name, self.app_version, self.app_changelog,
            self.app_archs, self.app_framework)
        self.mock_post.assert_called_once_with(
            upload_url, data={'version': self.app_version,
                              'architectures': self.app_archs,
                              'changelog': self.app_changelog,
                              'framework': self.app_framework})

    def test_get_upload_data_uses_environment_variable(self):
        upload_url = MYAPPS_API_ROOT_URL + "click-upload/%s/" % (
            self.app_name,)
        self.command.get_upload_data(
            self.app_name, self.app_version, self.app_changelog,
            self.app_archs, self.app_framework)
        self.mock_post.assert_called_once_with(
            upload_url, data={'version': self.app_version,
                              'architectures': self.app_archs,
                              'changelog': self.app_changelog,
                              'framework': self.app_framework})

    @patch('click_toolbelt.upload.Upload.get_oauth_session')
    def test_get_upload_data_with_invalid_session(self,
                                                  mock_get_oauth_session):
        mock_get_oauth_session.return_value = None
        result = self.command.get_upload_data(
            self.app_name, self.app_version, self.app_changelog,
            self.app_archs, self.app_framework)
        self.assertEqual(result, {'success': False,
                                  'errors': ['No valid credentials found.']})
        self.assertFalse(self.mock_post.called)


class MarkUploadedTestCase(BaseUploadCommandTestCase):

    def setUp(self):
        super(MarkUploadedTestCase, self).setUp()

        patcher = patch('click_toolbelt.upload.Upload.get_oauth_session')
        mock_session = patcher.start()
        self.mock_post = mock_session.return_value.post
        self.addCleanup(patcher.stop)

        mock_environ = {'MYAPPS_API_ROOT_URL': MYAPPS_API_ROOT_URL}
        patcher = patch('click_toolbelt.upload.os.environ', mock_environ)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_mark_uploaded(self):
        response_data = {'success': True, 'errors': []}
        response = Response()
        response.status_code = 200
        response.reason = 'OK'
        response._content = json.dumps(response_data).encode('utf-8')
        self.mock_post.return_value = response

        result = self.command.mark_uploaded(
            self.uploaded_callback_url, self.app_name, self.app_version, 42)
        self.assertEqual(result, response_data)
        self.mock_post.assert_called_once_with(
            self.uploaded_callback_url, data={'version': self.app_version,
                                              'binary': 42})

    @patch('click_toolbelt.upload.Upload.get_oauth_session')
    def test_mark_uploaded_with_invalid_session(self, mock_get_oauth_session):
        mock_get_oauth_session.return_value = None
        result = self.command.mark_uploaded(
            self.uploaded_callback_url, self.app_name, self.app_version, 42)
        self.assertEqual(result, {'success': False,
                                  'errors': ['No valid credentials found.']})
        self.assertFalse(self.mock_post.called)

    def test_mark_uploaded_unsuccessful(self):
        response_data = {'foo': 'bar'}
        response = Response()
        response.status_code = 500
        response.reason = 'INTERNAL SERVER ERROR'
        response._content = json.dumps(response_data).encode('utf-8')
        self.mock_post.return_value = response

        result = self.command.mark_uploaded(
            self.uploaded_callback_url, self.app_name, self.app_version, 42)
        self.assertEqual(result, {'success': False,
                                  'errors': [json.dumps(response_data)]})
        self.mock_post.assert_called_once_with(
            self.uploaded_callback_url, data={'version': self.app_version,
                                              'binary': 42})

    @patch('click_toolbelt.upload.Upload.log')
    def test_mark_uploaded_error_during_post(self, mock_log):
        self.mock_post.side_effect = Exception('the error')

        result = self.command.mark_uploaded(
            self.uploaded_callback_url, self.app_name, self.app_version, 42)
        self.assertEqual(result, {'success': False, 'errors': ['the error']})
        self.mock_post.assert_called_once_with(
            self.uploaded_callback_url, data={'version': self.app_version,
                                              'binary': 42})
        mock_log.exception.assert_called_once_with(
            "There was an error marking application '%s' version '%s' "
            "as uploaded.", self.app_name, self.app_version)


class UploadCommandTestCase(BaseUploadCommandTestCase):

    def setUp(self):
        super(UploadCommandTestCase, self).setUp()

        patcher = patch('click_toolbelt.upload.Upload.log')
        self.mock_log = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('click_toolbelt.upload.requests.post')
        self.mock_post = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('click_toolbelt.upload.Upload.get_upload_data')
        self.mock_get_upload_data = patcher.start()
        self.mock_get_upload_data.return_value = {
            'success': True,
            'errors': [],
            'binary_path': '/path/to/binary',
            'source_path': '/path/to/source',
            'signature': 'signature',
            'application_id': 1,
        }
        self.addCleanup(patcher.stop)

        patcher = patch('click_toolbelt.upload.open')
        self.mock_open = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('click_toolbelt.upload.os.path.getsize')
        patcher.start()
        self.addCleanup(patcher.stop)

        parsed_args = namedtuple(
            'parsed_args',
            'application_name, version, filename, changelog, arch, framework')

        filename = 'package.click'
        self.args = parsed_args(
            self.app_name, self.app_version, filename, self.app_changelog,
            self.app_archs, self.app_framework)

    def test_parser(self):
        parser = self.command.get_parser(__namespace__)
        cmd_args = ['application_name', 'version', 'filename', 'changelog']
        for i, name in enumerate(cmd_args):
            # argument 0 is builtin --help
            # start comparing from first extra argument
            self.assertEqual(parser._actions[i + 1].dest, name)
            self.assertTrue(parser._actions[i + 1].required)
        # framework is optional
        self.assertEqual(parser._actions[-2].dest, 'framework')
        self.assertFalse(parser._actions[-2].required)
        # arch is optional, and last param
        self.assertEqual(parser._actions[-1].dest, 'arch')
        self.assertFalse(parser._actions[-1].required)

    def test_take_action(self):
        response = Response()
        response.status_code = 200
        response._content = json.dumps({'successful': True}).encode(
            'utf-8')
        self.mock_post.return_value = response

        name = 'click_toolbelt.upload.Upload.mark_uploaded'
        with patch(name) as mock_mark_uploaded:
            mock_mark_uploaded.return_value = {'success': True}
            self.command.take_action(self.args)

        # assert request was made to get upload data
        # followed by an updown upload request
        self.mock_get_upload_data.assert_called_once_with(
            self.app_name, self.app_version, self.app_changelog,
            self.app_archs, self.app_framework)
        self.mock_post.assert_called_with(
            CLICK_UPDOWN_UPLOAD_URL,
            files={'binary': self.mock_open.return_value},
            data=self.mock_get_upload_data.return_value)
        self.mock_log.info.assert_called_with(
            'Click Package upload finished successfully.')

    def test_take_action_handles_error_while_getting_upload_data(self):
        response = Response()
        response.status_code = 200
        self.mock_post.return_value = response
        self.mock_get_upload_data.return_value = {
            'success': False, 'errors': ['Some error']}

        self.command.take_action(self.args)

        self.mock_log.error.assert_called_with(
            'Error verifying upload request. Uploading not possible.\n'
            'Reason: %s', 'Some error')

    def test_take_action_handles_error_while_uploading(self):
        self.mock_post.side_effect = Exception('foo')

        self.command.take_action(self.args)

        self.mock_log.exception.assert_called_with(
            'There was an error uploading the click package.')

    def test_take_action_handles_unsuccessful_response(self):
        upload_response = {'success': True, 'errors': []}
        response = Response()
        response.status_code = 200
        response.reason = 'OK'
        response._content = json.dumps(upload_response).encode('utf-8')
        self.mock_post.return_value = response

        self.command.take_action(self.args)

        self.mock_log.error.assert_called_with(
            'There was an error uploading the click package.\n'
            'Reason: %s\n'
            'Text: %s',
            'OK', json.dumps(upload_response))

    def test_take_action_handles_error_response(self):
        response = Response()
        response.status_code = 500
        response.reason = 'INTERNAL SERVER ERROR'
        response._content = 'This is a traceback.'.encode('utf-8')
        self.mock_post.return_value = response

        self.command.take_action(self.args)

        self.mock_log.error.assert_called_with(
            'There was an error uploading the click package.\n'
            'Reason: %s\n'
            'Text: %s',
            'INTERNAL SERVER ERROR', 'This is a traceback.')

    def test_take_action_handles_unsuccessful_mark_uploaded_response(self):
        upload_response = {'successful': True, 'errors': []}
        response = Response()
        response.status_code = 200
        response.reason = 'OK'
        response._content = json.dumps(upload_response).encode('utf-8')
        self.mock_post.return_value = response

        name = 'click_toolbelt.upload.Upload.mark_uploaded'
        with patch(name) as mock_mark_uploaded:
            mock_mark_uploaded.return_value = {
                'success': False, 'errors': ['Please try again later']}
            self.command.take_action(self.args)

        self.mock_log.error.assert_called_with(
            'There was an error after uploading the click package.\n'
            'Reason: %s', 'Please try again later')
