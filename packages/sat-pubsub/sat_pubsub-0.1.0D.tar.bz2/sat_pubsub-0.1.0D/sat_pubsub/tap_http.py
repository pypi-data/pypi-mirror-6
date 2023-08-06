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

from twisted.application import internet, service, strports
from twisted.conch import manhole, manhole_ssh
from twisted.cred import portal, checkers
from twisted.web2 import channel, log, resource, server
from twisted.web2.tap import Web2Service

from sat_pubsub import gateway, tap
from sat_pubsub.gateway import RemoteSubscriptionService

class Options(tap.Options):
    optParameters = [
            ('webport', None, '8086', 'Web port'),
    ]



def getManholeFactory(namespace, **passwords):
    def getManHole(_):
        return manhole.Manhole(namespace)

    realm = manhole_ssh.TerminalRealm()
    realm.chainedProtocolFactory.protocolFactory = getManHole
    p = portal.Portal(realm)
    p.registerChecker(
            checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
    f = manhole_ssh.ConchFactory(p)
    return f



def makeService(config):
    s = tap.makeService(config)

    bs = s.getServiceNamed('backend')
    cs = s.getServiceNamed('component')

    # Set up XMPP service for subscribing to remote nodes

    if config['backend'] == 'pgsql':
        from sat_pubsub.pgsql_storage import GatewayStorage
        gst = GatewayStorage(bs.storage.dbpool)
    elif config['backend'] == 'memory':
        from sat_pubsub.memory_storage import GatewayStorage
        gst = GatewayStorage()

    ss = RemoteSubscriptionService(config['jid'], gst)
    ss.setHandlerParent(cs)
    ss.startService()

    # Set up web service

    root = resource.Resource()

    # Set up resources that exposes the backend
    root.child_create = gateway.CreateResource(bs, config['jid'],
                                               config['jid'])
    root.child_delete = gateway.DeleteResource(bs, config['jid'],
                                               config['jid'])
    root.child_publish = gateway.PublishResource(bs, config['jid'],
                                                 config['jid'])
    root.child_list = gateway.ListResource(bs)

    # Set up resources for accessing remote pubsub nodes.
    root.child_subscribe = gateway.RemoteSubscribeResource(ss)
    root.child_unsubscribe = gateway.RemoteUnsubscribeResource(ss)
    root.child_items = gateway.RemoteItemsResource(ss)

    if config["verbose"]:
        root = log.LogWrapperResource(root)

    site = server.Site(root)
    w = internet.TCPServer(int(config['webport']), channel.HTTPFactory(site))

    if config["verbose"]:
        logObserver = log.DefaultCommonAccessLoggingObserver()
        w2s = Web2Service(logObserver)
        w.setServiceParent(w2s)
        w = w2s

    w.setServiceParent(s)

    # Set up a manhole

    namespace = {'service': s,
                 'component': cs,
                 'backend': bs,
                 'root': root}

    f = getManholeFactory(namespace, admin='admin')
    manholeService = strports.service('2222', f)
    manholeService.setServiceParent(s)

    return s

