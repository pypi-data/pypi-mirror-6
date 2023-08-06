#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward" <cward@redhat.com>

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
