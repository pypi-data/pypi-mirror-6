# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
#!/usr/bin/env python
from setuptools import setup, find_packages

from click_toolbelt import __namespace__, __version__

try:
    long_description = open('README.txt', 'rt').read()
except IOError:
    long_description = ''


setup(
    name='click-toolbelt',
    version=__version__,

    description='Click App Toolbelt',
    long_description=long_description,

    author='Ricardo Kirkner',
    author_email='ricardo.kirkner@canonical.com',

    url='https://launchpad.net/click-toolbelt',
    download_url='https://launchpad.net/click-toolbelt',

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=[
        'cliff',
        'pyxdg',
        'requests-oauthlib',
        'requests',
        'ssoclient',
    ],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'click-toolbelt = click_toolbelt.toolbelt:main'
        ],
        __namespace__: [
            'login = click_toolbelt.login:Login',
            'upload = click_toolbelt.upload:Upload',
            'register = click_toolbelt.register:Register',
            'info = click_toolbelt.info:Info',
        ],
    },

    zip_safe=False,

    test_suite='click_toolbelt.tests',
    tests_require=[
        'mock',
    ],
)
