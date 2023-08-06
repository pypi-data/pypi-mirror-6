# Copyright 2014 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import json
import logging
import os
import time
from functools import wraps

from cliff.command import Command
from requests_oauthlib import OAuth1Session
from xdg.BaseDirectory import load_first_config

from click_toolbelt import __namespace__
from click_toolbelt.compat import ConfigParser, open, urljoin, urlparse
from click_toolbelt.constants import (
    CLICK_TOOLBELT_PROJECT_NAME,
    CLICK_UPDOWN_UPLOAD_URL,
    SCAN_STATUS_POLL_DELAY,
    SCAN_STATUS_POLL_RETRIES,
    UBUNTU_SSO_API_ROOT_URL,
)


def is_scan_completed(response):
    if response.ok:
        return response.json().get('completed', False)
    return False


class ClickToolbeltCommand(Command):

    def get_config(self):
        config_dir = load_first_config(CLICK_TOOLBELT_PROJECT_NAME)
        filename = os.path.join(config_dir, "%s.cfg" % __namespace__)
        parser = ConfigParser()
        if os.path.exists(filename):
            parser.read(filename)

        api_endpoint = os.environ.get(
            'UBUNTU_SSO_API_ROOT_URL', UBUNTU_SSO_API_ROOT_URL)
        location = urlparse(api_endpoint).netloc

        config = {}
        if parser.has_section(location):
            config.update(dict(parser.items(location)))
        return config

    def get_oauth_session(self):
        config = self.get_config()
        try:
            session = OAuth1Session(
                config['consumer_key'],
                client_secret=config['consumer_secret'],
                resource_owner_key=config['token_key'],
                resource_owner_secret=config['token_secret'],
                signature_method='PLAINTEXT',
            )
        except KeyError:
            session = None
        return session

    def take_action(self, parsed_args):
        pass


class ClickToolbeltUploadCommand(ClickToolbeltCommand):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ClickToolbeltUploadCommand, self).get_parser(
            prog_name)

        parser.add_argument('binary_filename')
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument('source_filename', nargs='?')
        source_group.add_argument('--source', metavar='source_filename',
                                  dest='source_filename')
        metadata_group = parser.add_mutually_exclusive_group()
        metadata_group.add_argument('metadata_filename', nargs='?')
        metadata_group.add_argument('--metadata', metavar='metadata_filename',
                                    dest='metadata_filename')

        return parser

    def read_metadata(self, metadata_filename):
        if metadata_filename:
            with open(metadata_filename, 'r') as metadata_file:
                # file is automatically closed by context manager
                metadata = json.load(metadata_file)
        else:
            metadata = {}

        return metadata

    def upload_files(self, binary_filename, source_filename=None):
        updown_url = os.environ.get('CLICK_UPDOWN_UPLOAD_URL',
                                    CLICK_UPDOWN_UPLOAD_URL)
        unscanned_upload_url = urljoin(updown_url, 'unscanned-upload/')
        files = {'binary': open(binary_filename, 'rb')}
        if source_filename is not None:
            files['source'] = open(source_filename, 'rb')

        result = {'success': False, 'errors': []}

        session = self.get_oauth_session()
        if session is None:
            result['errors'] = ['No valid credentials found.']
            return result

        try:
            response = session.post(
                unscanned_upload_url,
                files=files)
            if response.ok:
                response_data = response.json()
                result.update({
                    'success': response_data.get('successful', True),
                    'upload_id': response_data['upload_id'],
                    'binary_filesize': os.path.getsize(binary_filename),
                    'source_uploaded': 'source' in files,
                })
            else:
                self.log.error(
                    'There was an error uploading the click package.\n'
                    'Reason: %s\n'
                    'Text: %s',
                    response.reason, response.text)
                result['errors'] = [response.text]
        except Exception as err:
            self.log.exception(
                'An unexpected error was found while uploading files.')
            result['errors'] = [str(err)]
        finally:
            # make sure to close any open files used for request
            for fd in files.values():
                fd.close()

        return result

    def get_post_data(self, upload_data, metadata=None):
        data = {
            'updown_id': upload_data['upload_id'],
            'binary_filesize': upload_data['binary_filesize'],
            'source_uploaded': upload_data['source_uploaded'],
        }
        data.update({
            key: value
            for (key, value) in metadata.items()
            if key not in (
                # make sure not to override upload_id, binary_filesize and
                # source_uploaded
                'upload_id', 'binary_filesize', 'source_uploaded',
                # skip files as they will be added to the files argument
                'icon_256', 'icon', 'screenshots',
            )
        })
        return data

    def get_post_files(self, metadata=None):
        files = []

        icon = metadata.get('icon', metadata.get('icon_256', ''))
        if icon:
            icon_file = open(icon, 'rb')
            files.append(('icon_256', icon_file))

        screenshots = metadata.get('screenshots', [])
        for screenshot in screenshots:
            screenshot_file = open(screenshot, 'rb')
            files.append(('screenshots', screenshot_file))

        return files

    def get_scan_data(self, session, status_url):
        # initial retry after 10 seconds
        # linear backoff after that
        # abort after 5 retries
        @retry(terminator=is_scan_completed,
               retries=SCAN_STATUS_POLL_RETRIES,
               delay=SCAN_STATUS_POLL_DELAY,
               backoff=1, logger=self.log)
        def get_status():
            return session.get(status_url)

        response, aborted = get_status()

        completed = False
        data = {}
        if not aborted:
            completed = is_scan_completed(response)
            data = response.json()
        return completed, data


def retry(terminator=None, retries=3, delay=3, backoff=2, logger=None):
    """Decorate a function to automatically retry calling it on failure.

    Arguments:
        - terminator: this should be a callable that returns a boolean;
          it is used to determine if the function call was successful
          and the retry loop should be stopped
        - retries: an integer specifying the maximum number of retries
        - delay: initial number of seconds to wait for the first retry
        - backoff: exponential factor to use to adapt the delay between
          subsequent retries
        - logger: logging.Logger instance to use for logging

    The decorated function will return as soon as any of the following
    conditions are met:

        1. terminator evaluates function output as True
        2. there are no more retries left

    If the terminator callable is not provided, the function will be called
    exactly once and will not be retried.

    """
    def decorated(func):
        if retries != int(retries) or retries < 0:
            raise ValueError(
                'retries value must be a positive integer or zero')
        if delay < 0:
            raise ValueError('delay value must be positive')

        if backoff != int(backoff) or backoff < 1:
            raise ValueError('backoff value must be a positive integer')

        @wraps(func)
        def wrapped(*args, **kwargs):
            retries_left, current_delay = retries, delay

            result = func(*args, **kwargs)
            if terminator is not None:
                while not terminator(result) and retries_left > 0:
                    msg = "... retrying in %d seconds" % current_delay
                    if logger:
                        logger.warning(msg)

                    # sleep
                    time.sleep(current_delay)
                    retries_left -= 1
                    current_delay *= backoff

                    # retry
                    result = func(*args, **kwargs)
            return result, retries_left == 0

        return wrapped
    return decorated
