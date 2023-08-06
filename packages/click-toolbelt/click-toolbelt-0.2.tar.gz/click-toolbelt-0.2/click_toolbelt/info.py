# -*- coding: utf-8 -*-
# Copyright 2014 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import logging
import os

import requests
from cliff.command import Command

from click_toolbelt.constants import MYAPPS_API_ROOT_URL


class Info(Command):
    log = logging.getLogger(__name__)
    topics = ['version', 'department', 'license', 'country']

    def get_parser(self, prog_name):
        parser = super(Info, self).get_parser(prog_name)
        parser.add_argument('topic', nargs='?', choices=self.topics)
        return parser

    def get_info(self):
        result = {'success': False, 'errors': [], 'data': None}
        api_endpoint = os.environ.get(
            'MYAPPS_API_ROOT_URL', MYAPPS_API_ROOT_URL)
        response = requests.get(api_endpoint)
        if response.ok:
            result['success'] = True
            result['data'] = response.json()
        else:
            result['errors'] = [response.text]
        return result

    def get_version_info(self, data):
        return data.get('version')

    def get_department_info(self, data):
        return data.get('/dev/api/click-app/', {}).get('department')

    def get_license_info(self, data):
        return data.get('/dev/api/click-app/', {}).get('license')

    def get_country_info(self, data):
        return data.get('/dev/api/click-app/', {}).get('country')

    def get_topic_data(self, api_data, topic):
        method = getattr(self, 'get_{}_info'.format(topic))
        return method(api_data)

    def take_action(self, parsed_args):
        topic = parsed_args.topic
        result = self.get_info()

        if not result.get('success', False):
            self.log.info(
                'Could not get information. An error ocurred:\n\n%s\n\n',
                '\n'.join(result['errors']))
            return

        api_data = result['data']
        self.log.info('API info:')

        if topic:
            topics = [topic]
        else:
            topics = self.topics

        for topic in topics:
            data = self.get_topic_data(api_data, topic)
            if data:
                self.log.info('  %s: %s', topic, data)
