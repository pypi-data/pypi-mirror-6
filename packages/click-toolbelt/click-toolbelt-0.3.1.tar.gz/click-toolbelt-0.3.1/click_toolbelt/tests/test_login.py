# -*- coding: utf-8 -*-
# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
import os
import shutil
import tempfile
from collections import namedtuple
from unittest import TestCase
from xdg.BaseDirectory import save_config_path

from mock import patch
from requests import Response

from click_toolbelt import __namespace__
from click_toolbelt.compat import ConfigParser
from click_toolbelt.login import (
    CLICK_TOOLBELT_PROJECT_NAME,
    UBUNTU_SSO_API_ROOT_URL,
    Login,
)


class LoginCommandTestCase(TestCase):

    def setUp(self):
        super(LoginCommandTestCase, self).setUp()
        app = None
        args = None
        self.command = Login(app, args)
        self.email = 'user@domain.com'
        self.password = 'password'
        parsed_args = namedtuple('parsed_args', 'email, password, otp')
        self.parsed_args = parsed_args(self.email, self.password, '')

        # setup patches
        mock_environ = {
            'UBUNTU_SSO_API_ROOT_URL': UBUNTU_SSO_API_ROOT_URL,
        }
        patcher = patch('click_toolbelt.login.os.environ', mock_environ)
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('click_toolbelt.login.Login.log')
        self.mock_log = patcher.start()
        self.addCleanup(patcher.stop)

    def test_parser(self):
        parser = self.command.get_parser(__namespace__)
        for i, (name, required) in enumerate(
                [('email', True), ('password', True), ('otp', False)]):
            # argument 0 is builtin --help
            # start comparing from first extra argument
            self.assertEqual(parser._actions[i + 1].dest, name)
            self.assertEqual(parser._actions[i + 1].required, required)

    def setup_config_dir(self, include_click_dir=True):
        config_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, config_dir)
        patcher = patch('xdg.BaseDirectory.xdg_config_home',
                        config_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

        if include_click_dir:
            save_config_path(CLICK_TOOLBELT_PROJECT_NAME)
        return config_dir

    def test_save_config(self):
        config_dir = self.setup_config_dir()
        data = {'foo': '1', 'bar': '2', 'baz': '3'}
        expected_filename = os.path.join(config_dir,
                                         CLICK_TOOLBELT_PROJECT_NAME,
                                         "{}.cfg".format(__namespace__))

        self.command.save_config(data)

        cfg = ConfigParser()
        cfg.read(expected_filename)
        self.assertTrue(cfg.has_section('login.ubuntu.com'))
        self.assertEqual(dict(cfg.items('login.ubuntu.com')), data)

    def test_save_config_with_existing_data(self):
        config_dir = self.setup_config_dir()
        expected_filename = os.path.join(config_dir,
                                         CLICK_TOOLBELT_PROJECT_NAME,
                                         "{}.cfg".format(__namespace__))
        cfg = ConfigParser()
        cfg.add_section('login.ubuntu.com')
        cfg.set('login.ubuntu.com', 'foo', 'foo')
        cfg.write(open(expected_filename, 'w'))
        data = {'foo': '1', 'bar': '2', 'baz': '3'}

        self.command.save_config(data)

        cfg.read(expected_filename)
        self.assertTrue(cfg.has_section('login.ubuntu.com'))
        self.assertEqual(dict(cfg.items('login.ubuntu.com')), data)

    def test_config_dir_created_if_necessary(self):
        config_dir = self.setup_config_dir(include_click_dir=False)
        data = {'foo': '1', 'bar': '2', 'baz': '3'}
        expected_filename = os.path.join(config_dir,
                                         CLICK_TOOLBELT_PROJECT_NAME,
                                         "{}.cfg".format(__namespace__))

        self.command.save_config(data)

        cfg = ConfigParser()
        cfg.read(expected_filename)
        self.assertTrue(cfg.has_section('login.ubuntu.com'))
        self.assertEqual(dict(cfg.items('login.ubuntu.com')), data)

    @patch('ssoclient.v2.http.requests.Session.request')
    def test_take_action_successful(self, mock_post):
        token_data = {
            'consumer_key': 'consumer-key',
            'consumer_secret': 'consumer-secret',
            'token_key': 'token-key',
            'token_secret': 'token-secret',
        }
        response = Response()
        response.status_code = 201
        response._content = json.dumps(token_data).encode('utf-8')
        mock_post.return_value = response

        data = {
            'email': 'foo@foo.com',
            'password': 'password',
            'token_name': 'consumer-key',
        }
        result = self.command.login(data)
        expected = {'success': True, 'body': token_data}
        self.assertEqual(result, expected)

    @patch('ssoclient.v2.http.requests.Session.request')
    def test_take_action_unsuccessful_api_exception(self, mock_post):
        error_data = {
            'message': 'Error during login.',
            'code': 'INVALID_CREDENTIALS',
            'extra': {},
        }
        response = Response()
        response.status_code = 401
        response.reason = 'UNAUTHORISED'
        response._content = json.dumps(error_data).encode('utf-8')
        mock_post.return_value = response

        data = {
            'email': 'foo@foo.com',
            'password': 'password',
            'token_name': 'consumer-key',
        }
        result = self.command.login(data)
        expected = {'success': False, 'body': error_data}
        self.assertEqual(result, expected)

    @patch('ssoclient.v2.http.requests.Session.request')
    def test_take_action_unsuccessful_unexpected_error(self, mock_post):
        error_data = {
            'message': 'Error during login.',
            'code': 'UNEXPECTED_ERROR_CODE',
            'extra': {},
        }
        response = Response()
        response.status_code = 401
        response.reason = 'UNAUTHORISED'
        response._content = json.dumps(error_data).encode('utf-8')
        mock_post.return_value = response

        data = {
            'email': 'foo@foo.com',
            'password': 'password',
            'token_name': 'consumer-key',
        }
        result = self.command.login(data)
        expected = {'success': False, 'body': error_data}
        self.assertEqual(result, expected)

    @patch('click_toolbelt.login.Login.save_config')
    @patch('click_toolbelt.login.Login.login')
    def test_take_action_success(self, mock_login, mock_save_config):
        parsed_args = namedtuple('parsed_args', 'email, password, otp')
        args = parsed_args(self.email, self.password, '123456')
        login_data = {
            'email': self.email,
            'password': self.password,
            'token_name': CLICK_TOOLBELT_PROJECT_NAME,
            'otp': '123456',
        }
        token_data = {
            'consumer_key': 'consumer-key',
            'consumer_secret': 'consumer-secret',
            'token_key': 'token-key',
            'token_secret': 'token-secret',
        }

        mock_login.return_value = {
            'success': True,
            'body': token_data,
        }

        self.command.take_action(args)

        mock_login.assert_called_once_with(login_data)
        mock_save_config.assert_called_once_with(token_data)
        # assert output
        self.mock_log.info.assert_called_once_with('Login successful.')

    @patch('click_toolbelt.login.Login.save_config')
    @patch('click_toolbelt.login.Login.login')
    def test_take_action_failure(self, mock_login, mock_save_config):
        login_data = {
            'email': self.email,
            'password': self.password,
            'token_name': CLICK_TOOLBELT_PROJECT_NAME,
        }
        error_data = {
            'code': 'UNAUTHORISED',
            'message': 'Provided email/password is not correct.',
            'extra': {},
        }

        mock_login.return_value = {
            'success': False,
            'body': error_data,
        }

        self.command.take_action(self.parsed_args)

        mock_login.assert_called_once_with(login_data)
        self.assertFalse(mock_save_config.called)
        # assert output
        self.mock_log.info.assert_called_once_with(
            'Login failed.\n'
            'Reason: %s\n'
            'Detail: %s',
            'UNAUTHORISED', 'Provided email/password is not correct.')
