#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Copyright (c) 2003-2011 Ralph Meijer
Copyright (c) 2012, 2013 Jérôme Poisson


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
--

This program is based on Idavoll (http://idavoll.ik.nu/),
originaly written by Ralph Meijer (http://ralphm.net/blog/)
It is sublicensed under AGPL v3 (or any later version) as allowed by the original
license.

--

Here is a copy of the original license:

Copyright (c) 2003-2011 Ralph Meijer

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from twisted.application import service
from twisted.python import usage
from twisted.words.protocols.jabber.jid import JID

from wokkel.component import Component
from wokkel.disco import DiscoHandler
from wokkel.generic import FallbackHandler, VersionHandler
from wokkel.iwokkel import IPubSubResource
from wokkel.pubsub import PubSubService

from sat_pubsub import __version__
from sat_pubsub.backend import BackendService
from sat_pubsub.remote_roster import RosterClient

class Options(usage.Options):
    optParameters = [
        ('jid', None, 'pubsub', 'JID this component will be available at'),
        ('secret', None, 'secret', 'Jabber server component secret'),
        ('rhost', None, '127.0.0.1', 'Jabber server host'),
        ('rport', None, '5347', 'Jabber server port'),
        ('backend', None, 'pgsql', 'Choice of storage backend'),
        ('dbuser', None, None, 'Database user (pgsql backend)'),
        ('dbname', None, 'pubsub', 'Database name (pgsql backend)'),
        ('dbpass', None, None, 'Database password (pgsql backend)'),
        ('dbhost', None, None, 'Database host (pgsql backend)'),
        ('dbport', None, None, 'Database port (pgsql backend)'),
    ]

    optFlags = [
        ('verbose', 'v', 'Show traffic'),
        ('hide-nodes', None, 'Hide all nodes for disco')
    ]

    def postOptions(self):
        if self['backend'] not in ['pgsql', 'memory']:
            raise usage.UsageError, "Unknown backend!"

        self['jid'] = JID(self['jid'])



def makeService(config):
    s = service.MultiService()

    # Create backend service with storage

    if config['backend'] == 'pgsql':
        from twisted.enterprise import adbapi
        from sat_pubsub.pgsql_storage import Storage
        dbpool = adbapi.ConnectionPool('psycopg2',
                                       user=config['dbuser'],
                                       password=config['dbpass'],
                                       database=config['dbname'],
                                       host=config['dbhost'],
                                       port=config['dbport'],
                                       cp_reconnect=True,
                                       client_encoding='utf-8',
                                       )
        st = Storage(dbpool)
    elif config['backend'] == 'memory':
        from sat_pubsub.memory_storage import Storage
        st = Storage()

    bs = BackendService(st)
    bs.setName('backend')
    bs.setServiceParent(s)

    # Set up XMPP server-side component with publish-subscribe capabilities

    cs = Component(config["rhost"], int(config["rport"]),
                   config["jid"].full(), config["secret"])
    cs.setName('component')
    cs.setServiceParent(s)

    cs.factory.maxDelay = 900

    if config["verbose"]:
        cs.logTraffic = True

    FallbackHandler().setHandlerParent(cs)
    VersionHandler(u'SàT Pubsub', __version__).setHandlerParent(cs)
    DiscoHandler().setHandlerParent(cs)

    resource = IPubSubResource(bs)
    resource.hideNodes = config["hide-nodes"]
    resource.serviceJID = config["jid"]

    ps = PubSubService(resource)
    ps.setHandlerParent(cs)
    resource.pubsubService = ps

    rc = RosterClient()
    rc.setHandlerParent(cs)
    bs.roster = rc

    return s
