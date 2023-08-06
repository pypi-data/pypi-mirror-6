# Copyright 2014 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import os
import time
from functools import wraps

from cliff.command import Command
from requests_oauthlib import OAuth1Session
from xdg.BaseDirectory import load_first_config

from click_toolbelt import __namespace__
from click_toolbelt.compat import ConfigParser, urlparse
from click_toolbelt.constants import (
    CLICK_TOOLBELT_PROJECT_NAME,
    UBUNTU_SSO_API_ROOT_URL,
)


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
