#!/usr/bin/python
#-*- coding: utf-8 -*-
#
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

"""
Remote roster client.

This module access roster throught a hacked version of
remote roster management http://jkaluza.fedorapeople.org/remote-roster.html
"""

from wokkel import xmppim
from wokkel.compat import IQ
from twisted.words.xish import domish

NS_ROSTER = 'jabber:iq:roster'

class RosterClient(xmppim.RosterClientProtocol):
    """Similar to classic RosterClient, but we can get any jid managed by the host server"""
    #FIXME: need to manage updates, and database sync
    #TODO: cache

    def getRoster(self, to_jid):
        """
        Retrieve contact list.

        @return: Roster as a mapping from L{JID} to L{RosterItem}.
        @rtype: L{twisted.internet.defer.Deferred}
        """

        def processRoster(result):
            roster = {}
            for element in domish.generateElementsQNamed(result.query.children,
                                                         'item', NS_ROSTER):
                item = xmppim.RosterItem.fromElement(element)
                roster[item.entity] = item

            return roster

        iq = IQ(self.xmlstream, 'get')
        iq.addElement((NS_ROSTER, 'query'))
        iq["to"] = to_jid.userhost()
        d = iq.send()
        d.addCallback(processRoster)
        return d

    
