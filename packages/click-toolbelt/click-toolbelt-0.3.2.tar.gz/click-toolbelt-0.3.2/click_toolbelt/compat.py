# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3 (see the file LICENSE).
from __future__ import absolute_import, unicode_literals
import sys


PY2 = sys.version_info[0] == 2
if PY2:
    from __builtin__ import open  # noqa
    from ConfigParser import ConfigParser  # noqa
    from urlparse import urljoin  # noqa
    from urlparse import urlparse  # noqa
else:
    from builtins import open  # noqa
    from configparser import ConfigParser  # noqa
    from urllib.parse import urljoin  # noqa
    from urllib.parse import urlparse  # noqa
