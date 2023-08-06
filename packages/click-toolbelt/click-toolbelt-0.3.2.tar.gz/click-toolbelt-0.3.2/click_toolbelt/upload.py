# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import logging
import os
import re

import requests

from click_toolbelt.common import (
    ClickToolbeltCommand,
    ClickToolbeltUploadCommand,
)
from click_toolbelt.compat import open, urljoin
from click_toolbelt.constants import (
    CLICK_UPDOWN_UPLOAD_URL,
    MYAPPS_API_ROOT_URL,
)


class Upload(ClickToolbeltUploadCommand):
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('Running scan-upload command...')

        binary_filename = parsed_args.binary_filename
        source_filename = parsed_args.source_filename
        metadata_filename = parsed_args.metadata_filename

        self.upload_with_scan(binary_filename, source_filename,
                              metadata_filename)

    def upload_with_scan(self, binary_filename, source_filename,
                         metadata_filename):

        # validate package filename
        pattern = (r'(.*/)?(?P<name>[\w\-_\.]+)_'
                   '(?P<version>[\d\.]+)_(?P<arch>\w+)\.click')
        match = re.match(pattern, binary_filename)
        if not match:
            self.log.info('Invalid click package filename.')
            return
        name = match.groupdict()['name']

        self.log.info('Uploading files...')
        data = self.upload_files(binary_filename,
                                 source_filename=source_filename)
        success = data.get('success', False)
        errors = data.get('errors', [])
        if not success:
            self.log.info('Upload failed:\n\n%s\n', '\n'.join(errors))
            return

        self.log.info('Uploading new version...')
        result = self.upload_app(
            name, data, metadata=self.read_metadata(metadata_filename))
        success = result.get('success', False)
        errors = result.get('errors', [])
        app_url = result.get('application_url', '')

        if success:
            self.log.info('Application uploaded successfully.')
        else:
            self.log.info('Upload did not complete.')

        if errors:
            self.log.info('Some errors were detected:\n\n%s\n\n',
                          '\n'.join(errors))

        if app_url:
            self.log.info('Please check out the application at: %s.\n',
                          app_url)

    def upload_app(self, name, upload_data, metadata=None):
        myapps_api_url = os.environ.get('MYAPPS_API_ROOT_URL',
                                        MYAPPS_API_ROOT_URL)
        upload_url = urljoin(myapps_api_url, "click-upload/%s/" % name)

        result = {'success': False, 'errors': [], 'application_url': ''}

        session = self.get_oauth_session()
        if session is None:
            result['errors'] = ['No valid credentials found.']
            return result

        if metadata is None:
            metadata = {}

        try:
            data = self.get_post_data(upload_data, metadata=metadata)
            # trigger package scan
            data.update({'extract': '1'})
            files = self.get_post_files(metadata=metadata)

            response = session.post(upload_url, data=data, files=files)
            if response.ok:
                response_data = response.json()
                status_url = response_data['status_url']
                self.log.info('Package submitted to %s', upload_url)
                self.log.info('Checking package status...')
                completed, data = self.get_scan_data(session, status_url)
                if completed:
                    self.log.info('Package scan completed.')
                    message = data.get('message', '')
                    if not message:
                        result['success'] = True
                    else:
                        result['errors'] = [message]
                else:
                    result['errors'] = [
                        'Package scan took too long.',
                    ]
                    status_web_url = response_data.get('web_status_url')
                    if status_web_url:
                        result['errors'].append(
                            'Please check the status later at: %s.' % (
                                status_web_url),
                        )
                result['application_url'] = data.get('application_url', '')
            else:
                self.log.error(
                    'There was an error uploading the application.\n'
                    'Reason: %s\n'
                    'Text: %s',
                    response.reason, response.text)
                result['errors'] = [response.text]
        except Exception as err:
            self.log.exception(
                'There was an error uploading the application.')
            result['errors'] = [str(err)]
        finally:
            # make sure to close any open files used for request
            for fname, fd in files:
                fd.close()

        return result
