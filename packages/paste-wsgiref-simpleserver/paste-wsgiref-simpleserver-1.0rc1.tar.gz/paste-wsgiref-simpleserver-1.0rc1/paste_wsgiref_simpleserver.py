# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of paste-wsgiref-simpleserver
# <https://github.com/2degrees/paste-wsgiref-simpleserver>, which is subject
# to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

from wsgiref.simple_server import make_server as make_wsgiref_server

from paste.deploy.converters import asint


def run_simple_server(wsgi_app, global_conf, host='127.0.0.1', port=8080):
    port = asint(port)
    server = make_wsgiref_server(host, port, wsgi_app)
    server.serve_forever()
