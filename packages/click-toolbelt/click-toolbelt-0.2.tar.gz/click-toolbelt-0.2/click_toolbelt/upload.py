# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import logging
import os

import requests

from click_toolbelt.common import ClickToolbeltCommand
from click_toolbelt.compat import open, urljoin
from click_toolbelt.constants import (
    CLICK_UPDOWN_UPLOAD_URL,
    MYAPPS_API_ROOT_URL,
)


class Upload(ClickToolbeltCommand):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Upload, self).get_parser(prog_name)
        parser.add_argument('application_name')
        parser.add_argument('version')
        parser.add_argument('filename')
        parser.add_argument('changelog')
        parser.add_argument('framework', nargs='?')
        parser.add_argument(
            'arch', nargs='*', default='all',
            choices=['armhf', 'i386', 'amd64', 'all'])
        return parser

    def get_upload_data(
            self, name, version, changelog, architectures, framework):
        myapps_url = os.environ.get('MYAPPS_API_ROOT_URL', MYAPPS_API_ROOT_URL)
        myapps_url = urljoin(myapps_url, 'click-upload/%s/' % name)

        result = {'success': False, 'errors': []}

        session = self.get_oauth_session()
        if session is None:
            result['errors'] = ['No valid credentials found.']
            return result

        try:
            response = session.post(
                myapps_url,
                data={'version': version, 'changelog': changelog,
                      'architectures': architectures, 'framework': framework})
            if response.ok:
                result.update(response.json())
            else:
                result['errors'] = [response.text]
        except Exception as err:
            self.log.exception("There was an error getting upload data for "
                               "application '%s' version '%s'.", name, version)
            result['errors'] = [str(err)]
        return result

    def mark_uploaded(self, uploaded_callback_url, name, version, binary_size):
        result = {'success': False, 'errors': []}

        data = {
            'version': version,
            'binary': binary_size,
        }

        session = self.get_oauth_session()
        if session is None:
            result['errors'] = ['No valid credentials found.']
            return result

        try:
            response = session.post(uploaded_callback_url, data=data)
            if response.ok:
                result.update(response.json())
            else:
                result['errors'] = [response.text]
        except Exception as err:
            self.log.exception("There was an error marking application '%s' "
                               "version '%s' as uploaded.", name, version)
            result['errors'] = [str(err)]
        return result

    def take_action(self, parsed_args):
        self.log.info('Running upload command...')

        application_name = parsed_args.application_name
        version = parsed_args.version
        filename = parsed_args.filename
        changelog = parsed_args.changelog
        architectures = parsed_args.arch
        framework = parsed_args.framework

        data = self.get_upload_data(
            application_name, version, changelog, architectures, framework)
        if not data.get('success', False):
            errors = data.get('errors', ['Unknown error'])
            self.log.error(
                'Error verifying upload request. Uploading not possible.\n'
                'Reason: %s', '\n'.join(errors))
            return

        uploaded_callback_url = data.pop('uploaded_callback_url', None)
        files = {'binary': open(filename, 'rb')}

        # do the request
        upload_url = os.environ.get('CLICK_UPDOWN_UPLOAD_URL',
                                    CLICK_UPDOWN_UPLOAD_URL)

        success = False
        response = None
        try:
            response = requests.post(upload_url, data=data, files=files)
            if response.ok:
                data = response.json()
                success = data.get('successful', False)
        except Exception:
            self.log.exception(
                'There was an error uploading the click package.')
            return

        if success:
            binary_size = os.path.getsize(filename)
            data = self.mark_uploaded(uploaded_callback_url, application_name,
                                      version, binary_size)
            if data.get('success', False):
                self.log.info('Click Package upload finished successfully.')
            else:
                errors = data.get('errors', ['Unknown error'])
                self.log.error(
                    'There was an error after uploading the click package.\n'
                    'Reason: %s', '\n'.join(errors))
        else:
            self.log.error(
                'There was an error uploading the click package.\n'
                'Reason: %s\n'
                'Text: %s',
                response.reason, response.text)
