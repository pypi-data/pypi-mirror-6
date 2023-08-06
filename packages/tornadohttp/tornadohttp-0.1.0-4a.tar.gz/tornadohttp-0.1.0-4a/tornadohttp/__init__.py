#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward" <cward@redhat.com>

from __future__ import unicode_literals

from ._version import __version__, version_info
# touch it to avoid pep8 error 'imported but unused'
__version__, version_info

import logging
log_format = "%(name)s.%(process)s:%(asctime)s:%(message)s"
log_format = logging.Formatter(log_format)
logger = logging.getLogger()
logger.setLevel(logging.WARN)
hdlr = logging.StreamHandler()
hdlr.setFormatter(log_format)
logger.addHandler(hdlr)

from tornadohttp import TornadoHTTP
TornadoHTTP  # avoid pyflakes 'imported but unused' error
