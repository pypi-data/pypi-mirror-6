# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import sys


PY2 = sys.version_info[0] == 2
if PY2:
    from __builtin__ import open
    from ConfigParser import ConfigParser
    from urlparse import urljoin
    from urlparse import urlparse
else:
    from builtins import open
    from configparser import ConfigParser
    from urllib.parse import urljoin
    from urllib.parse import urlparse
