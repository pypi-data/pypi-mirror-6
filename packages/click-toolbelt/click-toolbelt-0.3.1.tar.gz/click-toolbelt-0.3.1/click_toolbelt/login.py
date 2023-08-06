# -*- coding: utf-8 -*-
# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import logging
import os

from cliff.command import Command
from ssoclient.v2 import (
    ApiException,
    UnexpectedApiError,
    V2ApiClient,
)
from xdg.BaseDirectory import save_config_path

from click_toolbelt import __namespace__
from click_toolbelt.constants import (
    CLICK_TOOLBELT_PROJECT_NAME,
    UBUNTU_SSO_API_ROOT_URL,
)
from click_toolbelt.compat import ConfigParser, urlparse


class Login(Command):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Login, self).get_parser(prog_name)
        parser.add_argument('email')
        parser.add_argument('password')
        parser.add_argument('otp', nargs='?')
        return parser

    def save_config(self, data):
        config_dir = save_config_path(CLICK_TOOLBELT_PROJECT_NAME)

        filename = os.path.join(config_dir, "%s.cfg" % __namespace__)
        parser = ConfigParser()
        if os.path.exists(filename):
            parser.read(filename)

        api_endpoint = os.environ.get(
            'UBUNTU_SSO_API_ROOT_URL', UBUNTU_SSO_API_ROOT_URL)
        location = urlparse(api_endpoint).netloc
        if not parser.has_section(location):
            parser.add_section(location)

        for key, value in data.items():
            parser.set(location, key, value)

        parser.write(open(filename, 'w'))

    def login(self, data):
        result = {
            'success': False,
            'body': None,
        }

        api_endpoint = os.environ.get(
            'UBUNTU_SSO_API_ROOT_URL', UBUNTU_SSO_API_ROOT_URL)
        client = V2ApiClient(endpoint=api_endpoint)
        try:
            response = client.login(data=data)
            result['body'] = response
            result['success'] = True
        except ApiException as err:
            result['body'] = err.body
        except UnexpectedApiError as err:
            result['body'] = err.json_body
        return result

    def take_action(self, parsed_args):
        login_data = {
            'email': parsed_args.email,
            'password': parsed_args.password,
            'token_name': CLICK_TOOLBELT_PROJECT_NAME,
        }
        if parsed_args.otp:
            login_data['otp'] = parsed_args.otp

        response = self.login(login_data)
        if response.get('success', False):
            self.log.info('Login successful.')
            self.save_config(response['body'])
        else:
            error = response['body']
            self.log.info(
                'Login failed.\n'
                'Reason: %s\n'
                'Detail: %s',
                error['code'], error['message'])
