# -*- coding: utf-8 -*-

"""Declare `application` for WSGI Servers"""

import slingr.server

application = slingr.server.Server.wsgi()
