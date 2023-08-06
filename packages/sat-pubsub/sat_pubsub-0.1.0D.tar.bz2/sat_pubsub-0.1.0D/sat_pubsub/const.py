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


NS_GROUPBLOG_PREFIX = 'urn:xmpp:groupblog:'
NS_ITEM_CONFIG = "http://jabber.org/protocol/pubsub#item-config"
OPT_ACCESS_MODEL = 'pubsub#access_model'
OPT_ROSTER_GROUPS_ALLOWED = 'pubsub#roster_groups_allowed'
OPT_PUBLISH_MODEL = 'pubsub#publish_model'
VAL_AMODEL_OPEN = 'open'
VAL_AMODEL_ROSTER = 'roster'
VAL_AMODEL_JID = 'jid'
VAL_AMODEL_DEFAULT = VAL_AMODEL_OPEN
VAL_PMODEL_PUBLISHERS = 'publishers'
VAL_PMODEL_SUBSCRIBERS = 'subscribers'
VAL_PMODEL_OPEN = 'open'
VAL_PMODEL_DEFAULT = VAL_PMODEL_PUBLISHERS

FLAG_RETRACT_ALLOW_PUBLISHER = True  # XXX: see the method BackendService._doRetractAllowPublisher
